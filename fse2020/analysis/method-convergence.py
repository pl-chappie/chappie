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

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('-work-directory')
    args = parser.parse_args()

    data_path = args.work_directory
    plots_path = os.path.join(data_path, 'plots')
    if not os.path.exists(plots_path):
        os.mkdir(plots_path)

    rates = pd.read_csv(os.path.join(data_path, '.calm-rates'), delimiter = ' ', header = None)
    rates.columns = ['bench', 'size', 'rate']
    rates = rates.set_index('bench').rate.to_dict()

    calm_data = os.path.join(data_path, 'calmness', 'calm')
    profile_data = os.path.join(data_path, 'profiling')
    file_from = lambda k: os.path.join('raw', str(k))

    benchs = np.sort(os.listdir(calm_data))
    benchs_ = tqdm(benchs)

    summary = []
    for bench in benchs_:
        benchs_.set_description(bench)

        if not os.path.exists(os.path.join(plots_path, bench)):
            os.mkdir(os.path.join(plots_path, bench))

        df = pd.concat([pd.read_csv(
            os.path.join(profile_data, bench, str(n), 'summary', 'method.csv')
        ).assign(batch = n) for n in os.listdir(os.path.join(profile_data, bench))])

        batches = df.batch.max()

        df['method'] = df.trace.str.split(';').str[0]
        df = df.groupby(['method', 'batch']).energy.sum()
        df = df.reset_index()

        df = pd.concat([
            df[df.batch < df.batch.max()].assign(g = 0),
            df.assign(g = 1)
        ])
        df = df.groupby(['method', 'g']).energy.sum()
        df = df.unstack()
        df = df / df.sum()

        corr = df.corr().loc[0, 1]
        corr_err = np.sqrt((1 - corr ** 2) / (len(df) - 2))

        rms = (df[0] - df[1]) ** 2 / len(df)
        rms = np.sqrt(rms.sum())

        summary.append(pd.Series(
            index = ['bench', 'batches', 'pcc', 'pcc_err', 'rmse'],
            data = [bench, batches, corr, corr_err, rms]
        ))

    df = pd.concat(summary, axis = 1).T.set_index('bench').astype(float).round(4)
    df.batches = df.batches.astype(int)
    df['rate'] = df.index.map(rates)
    df = df[['rate', 'batches', 'pcc', 'pcc_err', 'rmse']]

    df.index = df.index.map(lambda x: r'\texttt{' + x + '}')
    df = df.reset_index().transform(lambda x: x.map('{} & '.format)).sum(axis = 1).str[:-1].map(lambda x: x[:-1] + ' \\\\\n')
    table = df.values

    with open(os.path.join(plots_path, 'convergence-table.tex'), 'w') as f:
        [f.write(row) for row in table]

if __name__ == '__main__':
    main()
