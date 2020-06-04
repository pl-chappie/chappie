#!/usr/bin/python3

import argparse
import json
import os

import numpy as np
import pandas as pd

from tqdm import tqdm

bench_sizes = {
    'biojava': 'default',
    'jython': 'default',
    'xalan': 'default',
    'avrora': 'large',
    'batik': 'large',
    'eclipse': 'large',
    'h2': 'large',
    'pmd': 'large',
    'sunflow': 'large',
    'tomcat': 'large',
    'graphchi': 'huge',
}

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

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('-d', '--data-directory')
    args = parser.parse_args()

    calm_data = os.path.join(args.data_directory, 'calmness', 'calm')
    profile_data = os.path.join(args.data_directory, 'calmness', 'profile')
    file_from = lambda k: os.path.join('raw', str(k))

    benchs = np.sort(os.listdir(calm_data))

    df = []
    for bench in benchs:
        idx = ('benchmark', 'size', 'rate', 'runtime', 'runtime_std', 'temporal', 'temporal_err', 'temporal_rms', 'spatial', 'spatial_err', 'spatial_rms')

        runs = np.sort(os.listdir(os.path.join(calm_data, bench, 'raw')))
        runs = runs[(len(runs) // 5):]

        time_files = lambda run: os.path.join(calm_data, bench, file_from(run), 'time.json')
        temporal_files = lambda run: os.path.join(calm_data, bench, file_from(run), 'freqs.csv')

        t_ref = parse_runtime(time_files, runs)
        f_ref = parse_freqs(temporal_files, runs)

        for rate in os.listdir(os.path.join(profile_data, bench)):
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

            tc = {'corr': f.corr(ref)}
            tc['err'] = np.sqrt((1 - tc['corr'] ** 2) / (len(f) - 2))
            tc['rms'] = np.sqrt(((f.min() - f.max())**2).sum() / len(f))

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

            sc = {'corr': f.corr(ref)}
            sc['err'] = np.sqrt((1 - sc['corr'] ** 2) / (len(f) - 2))
            sc['rms'] = np.sqrt(((f.min() - f.max())**2).sum() / len(f))

            df.append(pd.Series(index = idx, data = (bench, bench_sizes[bench], int(rate), t['mean'], t['std'], tc['corr'], tc['err'], tc['rms'], sc['corr'], sc['err'], sc['rms'])))

    plots_path = os.path.join(args.data_directory, 'plots')
    if not os.path.exists(plots_path):
        os.mkdir(plots_path)

    df = pd.concat(df, axis = 1).T.set_index(['benchmark', 'size', 'rate']).sort_index()
    df.to_csv(os.path.join(plots_path, 'calmness.csv'))

    rates = df.reset_index()
    optimal_rates = rates[((abs(rates.runtime) < 0.05) | (abs(rates.runtime) <= 2 * rates.runtime_std)) & (rates.temporal > 0.85) & (rates.spatial > 0.85)]
    optimal_rates = optimal_rates[optimal_rates.groupby('benchmark').rate.apply(lambda x: x == x.min())]
    lowest_rates = rates[rates.groupby('benchmark').rate.apply(lambda x: x == x.min()) & ~rates.benchmark.isin(optimal_rates.benchmark)]
    rates = pd.concat([optimal_rates, lowest_rates]).set_index('benchmark').sort_index().reset_index()
    f = open(os.path.join(args.data_directory, '.calm-rates'), 'w')
    for bench, size, rate in rates[['benchmark', 'size', 'rate']].values:
        f.write(' '.join([bench, size, str(rate)]) + '\n')
    f.close()

if __name__ == '__main__':
    main()
