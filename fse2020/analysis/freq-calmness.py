#!/usr/bin/python3

import argparse
import json
import os

import numpy as np
import pandas as pd

import matplotlib
matplotlib.use('Agg')

import matplotlib.pyplot as plt
import matplotlib.ticker as mtick

from tqdm import tqdm

def parse_timestamp(path):
    ts = np.sort([int(t) for t in json.load(open(path)).values()])
    return (np.max(ts) - np.min(ts)) / 100000000000

def parse_runtime(path, runs):
    t = [parse_timestamp(path(run)) for run in runs]
    return {'mean': np.mean(t), 'std': np.std(t)}

def parse_freqs(path, runs):
    df = pd.concat([pd.read_csv(path(run), delimiter = ';').assign(run = int(run)) for run in runs])
    df.freq /= 10000
    df.freq = df.freq.astype(int)

    df.epoch = df.epoch * df.epoch.max() / df.groupby('run').epoch.max().mean()
    df.epoch = df.epoch.round(0).astype(int)

    return df

def time_calmness(t, ref):
    return {
        'mean': (t['mean'] - ref['mean']) / ref['mean'],
        'std': np.sqrt((t['mean'] * t['std'])**2 + (ref['mean'] * ref['std'])**2)
    }

def create_bins(s, n):
    iqr = s.quantile(0.75) - s.quantile(0.25)
    if iqr > 0:
        d = s.max() - s.min()
        size = int(d * np.cbrt(n) / iqr / 2)
    else:
        size = 21

    if size > 21:
        size = 21

    return np.linspace(s.min() - 0.01, s.max() + 0.01, size + 1)

def temporal_plot(df):
    df = df.to_frame().reset_index()
    df.freq = pd.cut(df.freq.map(lambda x: (x.left + x.right) / 2), bins = list(range(100, 276, 25)) + [350])
    df = df.groupby(['epoch', 'freq']).sum()
    df = df / df.sum()

    ax = df.unstack().plot.bar(
        stacked = True,
        width = 0.8,
        figsize = (10.5, 9)
    )

    handles, labels = ax.get_legend_handles_labels()
    ax.legend(handles[::-1], ['[1.0, 1.25)', '[1.25, 1.5)', '[1.5, 1.75)', '[1.75, 2.0)', '[2.0, 2.25)', '[2.25, 2.5)', '[2.5, 2.75)', '[2.75, 3.0)'][::-1], loc = 'lower right', fontsize = 20, title = 'frequency (GHz)')

    ax.spines['right'].set_visible(False)
    ax.spines['top'].set_visible(False)
    ax.spines['left'].set_visible(False)

    plt.xlabel('Epoch', fontsize = 32)
    plt.ylabel('')

    plt.xticks([])
    plt.yticks([])

def spatial_plot(df):
    df = df.to_frame().reset_index()
    df.freq = pd.cut(df.freq.map(lambda x: (x.left + x.right) / 2), bins = list(range(100, 276, 25)) + [350])
    df = df.groupby(['cpu', 'freq']).sum()
    df = df / df.sum()

    ax = (100 * df).unstack().plot.bar(
        stacked = True,
        width = 0.8,
        figsize = (10.5, 9)
    )

    handles, labels = ax.get_legend_handles_labels()
    ax.legend(handles[::-1], ['[1.0, 1.25)', '[1.25, 1.5)', '[1.5, 1.75)', '[1.75, 2.0)', '[2.0, 2.25)', '[2.25, 2.5)', '[2.5, 2.75)', '[2.75, 3.0)'][::-1], loc = 'lower right', fontsize = 20, title = 'frequency (GHz)')

    ax.spines['right'].set_visible(False)
    ax.spines['top'].set_visible(False)

    plt.xlabel('Cores Operating At Frequency', fontsize = 32)
    plt.ylabel('Chance of Occurance', fontsize = 32)

    ax.xaxis.set_major_locator(plt.MultipleLocator(4))
    ax.xaxis.set_minor_locator(plt.MultipleLocator(1))
    plt.xticks(range(0, 41, 4), range(0, 41, 4), rotation = 45, fontsize = 36)

    plt.ylim(0, 40)
    ax.yaxis.set_major_formatter(mtick.PercentFormatter())
    plt.yticks(fontsize = 36)

    plt.minorticks_on()

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('-work-directory')
    args = parser.parse_args()

    calm_data = os.path.join(args.work_directory, 'calmness', 'calm')
    profile_data = os.path.join(args.work_directory, 'calmness', 'profile')
    file_from = lambda k: os.path.join('raw', str(k))

    plots_path = os.path.join(args.work_directory, 'plots')
    if not os.path.exists(plots_path):
        os.mkdir(plots_path)

    benchs = np.sort(os.listdir(calm_data))
    benchs = tqdm(benchs)

    df = []
    for bench in benchs:
        benchs.set_description(bench)
        idx = ('benchmark', 'rate', 'runtime', 'runtime_std', 'temporal', 'temporal_err', 'temporal_rms', 'spatial', 'spatial_err', 'spatial_rms')

        runs = np.sort(os.listdir(os.path.join(calm_data, bench, 'raw')))
        runs = runs[(len(runs) // 5):]

        time_files = lambda run: os.path.join(calm_data, bench, file_from(run), 'time.json')
        temporal_files = lambda run: os.path.join(calm_data, bench, file_from(run), 'freqs.csv')

        t_ref = parse_runtime(time_files, runs)
        f_ref = parse_freqs(temporal_files, runs)

        for rate in os.listdir(os.path.join(profile_data, bench)):
            benchs.set_description(bench + ' - ' + rate)
            time_files = lambda run: os.path.join(profile_data, bench, rate, file_from(run), 'time.json')
            temporal_files = lambda run: os.path.join(profile_data, bench, rate, file_from(run), 'cpu.csv')

            t = time_calmness(parse_runtime(time_files, runs), t_ref)

            ref = f_ref.copy(deep = True)
            f = parse_freqs(temporal_files, runs)
            f.epoch = f.epoch * ref.epoch.max() / f.groupby('run').epoch.max().mean()
            f.epoch = f.epoch.round(0).astype(int)

            merged_data = pd.concat([f, ref], sort = False)
            bins = create_bins(merged_data.freq, len(merged_data))
            if len(bins) > 1:
                f.freq = pd.cut(f.freq, bins = bins)
                f = f.groupby(['epoch', 'freq']).cpu.count()
                f = f / f.groupby('epoch').sum()

                ref.freq = pd.cut(ref.freq, bins = bins)
                ref = ref.groupby(['epoch', 'freq']).cpu.count()
                ref = ref / ref.groupby('epoch').sum()
            elif len(bins) == 1:
                f = f.groupby(['epoch']).cpu.count()
                ref = ref.groupby(['epoch']).cpu.count()

            temporal_plot(f)
            plt.savefig(os.path.join(plots_path, bench, 'temporal-{}ms.pdf'.format(rate)), bbox_inches = 'tight')
            plt.close()

            tc = {'corr': f.corr(ref)}
            tc['err'] = np.sqrt((1 - tc['corr'] ** 2) / (len(f) - 2))
            tc['rms'] = np.sqrt(((f.min() - f.max())**2).sum() / len(f))

            tc_ref = ref

            merged_data = pd.concat([f, ref], sort = False)
            bins = create_bins(merged_data, len(merged_data))
            f = f.to_frame().reset_index()
            ref = ref.to_frame().reset_index()
            if len(bins) > 1:
                f.cpu = pd.cut(f.cpu, bins = bins, include_lowest = True)
                f = f.groupby(['freq', 'cpu']).epoch.count()

                ref['cpu'] = pd.cut(ref['cpu'], bins = bins, include_lowest = True)
                ref = ref.groupby(['freq', 'cpu']).epoch.count()
            elif len(bins) == 1:
                f = f.groupby(['freq']).cpu.count()
                ref = ref.groupby(['freq']).cpu.count()

            spatial_plot(f)
            plt.savefig(os.path.join(plots_path, bench, 'spatial-{}ms.pdf'.format(rate)), bbox_inches = 'tight')
            plt.close()

            sc = {'corr': f.corr(ref)}
            sc['err'] = np.sqrt((1 - sc['corr'] ** 2) / (len(f) - 2))
            sc['rms'] = np.sqrt(((f.min() - f.max())**2).sum() / len(f))

            sc_ref = ref

            df.append(pd.Series(index = idx, data = (bench, int(rate), t['mean'], t['std'], tc['corr'], tc['err'], tc['rms'], sc['corr'], sc['err'], sc['rms'])))

        benchs.set_description(bench + ' - ref')

        temporal_plot(tc_ref)
        plt.savefig(os.path.join(plots_path, bench, 'temporal-reference.pdf'.format(rate)), bbox_inches = 'tight')
        plt.close()

        spatial_plot(sc_ref)
        plt.savefig(os.path.join(plots_path, bench, 'spatial-reference.pdf'.format(rate)), bbox_inches = 'tight')
        plt.close()

    df = pd.concat(df, axis = 1).T.set_index(['benchmark', 'rate'])
    s = df.temporal.unstack().T
    s.index = s.index.astype(str)

    ax = s.plot.line(
        style = ['o-', 's-', 'D-', 'h-', 'v-', 'P-', '^-', 'H-', '<-', '*-', '>-', 'X-', 'd-'],
        ms = 21,
        figsize = (25, 10)
    )

    ax.set_xlim(-0.5, len(s) - 0.5)

    plt.legend(loc = 'upper right', fontsize = 20)

    plt.xlabel('Sampling Rate (ms)', fontsize = 36)
    plt.ylabel('Temporal Correspondence', fontsize = 36)

    plt.xticks(fontsize = 40, rotation = 30)
    plt.yticks(fontsize = 40)

    plt.savefig(os.path.join(plots_path, 'temporal-correlation.pdf'), bbox_inches = 'tight')
    plt.close()

    s = df.spatial.unstack().T
    s.index = s.index.astype(str)
    ax = s.plot.line(
        style = ['o-', 's-', 'D-', 'h-', 'v-', 'P-', '^-', 'H-', '<-', '*-', '>-', 'X-', 'd-'],
        ms = 21,
        figsize = (25, 10)
    )

    ax.set_xlim(-0.5, len(s) - 0.5)

    plt.legend(loc = 'upper right', fontsize = 20)

    plt.xlabel('Sampling Rate (ms)', fontsize = 36)
    plt.ylabel('Spatial Correspondence', fontsize = 36)

    plt.xticks(fontsize = 40, rotation = 30)
    plt.yticks(fontsize = 40)

    plt.savefig(os.path.join(plots_path, 'spatial-correlation.pdf'), bbox_inches = 'tight')
    plt.close()

if __name__ == '__main__':
    main()
