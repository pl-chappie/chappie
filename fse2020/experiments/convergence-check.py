#!/usr/bin/python3

import argparse
import os

import numpy as np
import pandas as pd

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('-d', '--data-directory')
    args = parser.parse_args()

    method_file = lambda batch: os.path.join(args.data_directory, batch, 'summary', 'method.csv')

    batches = np.sort(os.listdir(args.data_directory))
    ranking = pd.concat([pd.read_csv(method_file(batch)).assign(batch = int(batch)) for batch in batches])

    ranking['method'] = ranking.trace.str.split(';').str[0]
    ranking = ranking.groupby(['method', 'batch']).energy.sum()
    ranking = ranking.reset_index()

    df = pd.concat([
        ranking[ranking.batch < (len(batches) - 1)].assign(g = 0),
        ranking.assign(g = 1)
    ])
    df = df.groupby(['method', 'g']).energy.sum()
    df = df.unstack()
    df = df / df.sum()

    corr = df.corr().loc[0, 1]
    print(corr)

if __name__ == '__main__':
    main()
