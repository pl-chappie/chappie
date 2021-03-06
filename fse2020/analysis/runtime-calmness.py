#!/usr/bin/python3

import argparse
import json
import os

from itertools import product

import matplotlib
matplotlib.use('Agg')

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from tqdm import tqdm

def parse_timestamp(path):
    ts = np.sort([int(t) for t in json.load(open(path)).values()])
    return (np.max(ts) - np.min(ts)) / 100000000000

_RAPL_WRAPAROUND = 16384

def rapl_wrap_around(reading):
    if reading >= 0:
        return reading
    else:
        return max(reading + _RAPL_WRAPAROUND, 0)

def parse_energy(path):
    energy = pd.read_csv(path, delimiter = ';')

    energy.package = energy.groupby('socket').package.diff()
    energy.dram = energy.groupby('socket').dram.diff()

    energy.package = energy.package.map(rapl_wrap_around)
    energy.dram = energy.dram.map(rapl_wrap_around)
    energy = energy.fillna(0)

    return energy[['package', 'dram']].sum().sum()

def calmness_plot(df, color = 'blue', label = None):
    df.index = df.index.astype(str)
    ax = df.plot.line(
        y = 'mean',
        yerr = 'std',
        lw = 2,
        capsize = 10,
        capthick = 1,
        color = color,
        legend = False,
        figsize = (25, 10),
    )

    ax.set_xlim(-0.5, len(df) - 0.5)

    plt.xlabel('Sampling Rate (ms)', fontsize = 20)
    if label is None:
        plt.ylabel(label, fontsize = 20)

    plt.xticks(fontsize = 20, rotation = 30)
    plt.yticks(fontsize = 24)

    return ax.get_figure()

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('-work-directory')
    args = parser.parse_args()

    data_path = args.work_directory
    plots_path = os.path.join(data_path, 'plots')
    if not os.path.exists(plots_path):
        os.mkdir(plots_path)

    calm_data = os.path.join(data_path, 'calmness', 'calm')
    profile_data = os.path.join(data_path, 'calmness', 'profile')
    file_from = lambda k: os.path.join('raw', str(k))

    benchs = np.sort(os.listdir(calm_data))
    benchs = tqdm(benchs)

    summary = []
    for bench in benchs:
        benchs.set_description(bench + " - ref")

        if not os.path.exists(os.path.join(plots_path, bench)):
            os.mkdir(os.path.join(plots_path, bench))
        runs = np.sort(os.listdir(os.path.join(calm_data, bench, 'raw')))
        runs = runs[(len(runs) // 5):]

        df = []
        for rate in os.listdir(os.path.join(profile_data, bench)):
            benchs.set_description(bench + " - " + rate)

            e = [parse_energy(
                os.path.join(profile_data, bench, rate, file_from(k), 'energy.csv')
            ) for k in runs]

            t = [parse_timestamp(
                os.path.join(profile_data, bench, rate, file_from(k), 'time.json')
            ) for k in runs]

            d = {
                'e_m': np.mean(e),
                't_m': np.mean(t),
                'e_s': np.std(e),
                't_s': np.std(t),
            }

            d['p_m'] = d['e_m'] / d['t_m']
            d['p_s'] = d['p_m'] * np.sqrt((d['e_s'] / d['e_m'])**2 + (d['t_s'] / d['t_m'])**2)

            d['rate'] = int(rate)

            df.append(pd.Series(d))

        benchs.set_description(bench + " - summary")

        df = pd.concat(df, axis = 1).T.set_index('rate').sort_index()[['e_m', 'e_s', 't_m', 't_s', 'p_m', 'p_s']] * 100
        df.index = df.index.astype(int)
        df.columns = pd.MultiIndex.from_tuples(product(('energy', 'runtime', 'power'), ('mean', 'std')))
        summary.append(df['runtime'].assign(benchmark = bench))

        for col, color, label in zip(['energy', 'runtime', 'power'], [u'#2ca02c', u'#d62728', u'#1f77b4'], ['Energy (J)', 'Runtime (s)', 'Power (W)']):
            calmness_plot(df[col], color, label)
            plt.savefig(os.path.join(plots_path, bench, '{}.pdf'.format(col)), bbox_inches = 'tight')
            plt.close()

    df = pd.concat(summary).reset_index().set_index(['rate', 'benchmark'])['mean'].unstack()
    df.index = df.index.astype(str)

    ax = df.plot.line(
        style = ['o-', 's-', 'D-', 'h-', 'v-', 'P-', '^-', 'H-', '<-', '*-', '>-', 'X-', 'd-'],
        ms = 21,
        figsize = (25, 10)
    )

    ax.set_xlim(-0.5, len(df) - 0.5)

    plt.legend(loc = 'upper right', fontsize = 20)

    plt.xlabel('Sampling Rate (ms)', fontsize = 36)
    plt.ylabel('Runtime (ms)', fontsize = 36)

    plt.xticks(fontsize = 40, rotation = 30)
    plt.yticks(fontsize = 40)

    plt.savefig(os.path.join(plots_path, 'runtime.pdf'), bbox_inches = 'tight')
    plt.close()

if __name__ == '__main__':
    main()
