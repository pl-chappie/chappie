#!/usr/bin/python3

import argparse
import json
import os

from itertools import product

import matplotlib
matplotlib.use('Agg')

import matplotlib.patheffects as path_effects
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from tqdm import tqdm

def energy_plot(df):
    ax = df.plot.bar(y = 'mean', yerr = 'std', stacked = True, edgecolor = 'black', width = 0.55, figsize = (16, 9), error_kw = dict(lw = 2, capsize = 10, capthick = 1))

    handles, labels = ax.get_legend_handles_labels()
    ax.legend(handles[::-1], ['dram 2', 'cpu 2', 'dram 1', 'cpu 1'], loc = 'upper left', fontsize = 20)

    plt.xlabel('Benchmark', fontsize = 20)
    plt.ylabel('Energy (J)', fontsize = 20)

    plt.xticks(fontsize = 20, rotation = 30)
    plt.yticks(fontsize = 24)

def parse_timestamp(path):
    ts = np.sort([int(t) for t in json.load(open(path)).values()])
    return np.max(ts) - np.min(ts)

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

    energy = energy.groupby('socket')[['package', 'dram']].sum()

    energy['energy'] = energy.sum(axis = 1)
    return energy.energy

def filter_to_application_(trace):
    try:
        while len(trace) > 0:
            record = trace[0]
            exclude = False
            exclude = any((
                (r'.' not in record),
                (r'java.' in record and '.java\.' not in record),
                (r'javax.' in record and '.javax\.' not in record),
                (r'jdk.' in record and '.jdk\.' not in record),
                (r'sun.' in record and '.sun\.' not in record),
                (r'org.apache.commons.' in record and '.org.apache.commons\.' not in record),
                (r'<init>' in record),
                (r'.so' in record),
                (r'::' in record),
                (r'[' in record),
                (r']' in record)
            ))
            if not exclude:
                return trace
            else:
                trace.pop(0)
    except:
        pass

    return 'end'

def filter_to_application(df):
    mask = (df.trace == 'end') | df.trace.str.contains('chappie') | df.trace.str.contains('jlibc') | df.trace.str.contains('jrapl')
    df = df[~mask]
    df.trace = df.trace.str.split('@').map(filter_to_application_)
    method = df.trace.str[0]
    df = df[(df.trace != 'end') & (method != 'e') & ~(method.str.contains('org.dacapo.harness'))]

    return df

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
    profiling_data = os.path.join(data_path, 'profiling')
    file_from = lambda k: os.path.join('raw', str(k))

    benchs = np.sort(os.listdir(calm_data))
    benchs = tqdm(benchs)

    summary = []
    energy = []

    for bench in benchs:
        benchs.set_description(bench)
        runs = np.sort(os.listdir(os.path.join(calm_data, bench, 'raw')))
        runs = runs[(len(runs) // 5):]

        ts = np.mean([parse_timestamp(os.path.join(calm_data, bench, 'raw', str(k), 'time.json')) / 1000000000 for k in runs])
        total_threads = len(json.load(open(os.path.join(profiling_data, bench, '0', 'raw', '0', 'id.json'))))
        live_threads = np.mean([
            pd.read_csv(os.path.join(
                profiling_data, bench, n, 'raw', str(k), 'vm.csv'
            ), delimiter = ';').groupby('epoch').id.count().mean() for n, k in product(
                os.listdir(os.path.join(profiling_data, bench)), runs
        )])

        methods = [pd.read_csv(os.path.join(
            profiling_data, bench, n, 'raw', str(k), 'method.csv'
        ), delimiter = ';').trace.str.split('@').tolist() for n, k in product(
            os.listdir(os.path.join(profiling_data, bench)), runs
        )]
        methods = len({m for iter in methods for stack in iter for m in stack})

        s = pd.Series(
            index = ['bench', 'methods', 'total threads', 'active threads', 'execution time(s)'],
            data = [bench, int(methods), int(total_threads), int(live_threads), np.round(ts, 2)]
        )

        summary.append(s)

        df = pd.concat([
            pd.read_csv(os.path.join(profiling_data, bench, i, 'summary', 'component.csv')).assign(i = i) for i in os.listdir(os.path.join(profiling_data, bench))
        ]).groupby(['socket', 'i']).sum().groupby('socket').agg(('mean', 'std')).stack(0).reset_index()
        df.columns = ['socket', 'component', 'mean', 'std']
        df['bench'] = bench
        df['component'] = df['component'].str.replace('package', 'cpu')
        df = df.set_index(['bench', 'component', 'socket'])

        energy.append(df)

    df = pd.concat(summary, axis = 1).T.set_index('bench')

    df.index = df.index.map(lambda x: r'\texttt{' + x + '}')
    df = df.reset_index().transform(lambda x: x.map('{} & '.format)).sum(axis = 1).str[:-1].map(lambda x: x[:-1] + ' \\\\\n')
    table = df.values

    with open(os.path.join(plots_path, 'summary-table.tex'), 'w') as f:
        [f.write(row) for row in table]

    df = pd.concat(energy)

    energy_plot(df.unstack().unstack())

    plt.savefig(os.path.join(plots_path, 'energy.pdf'), bbox_inches = 'tight')
    plt.close()


if __name__ == '__main__':
    main()
