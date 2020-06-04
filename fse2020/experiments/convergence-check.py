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

# #!/usr/bin/python3
#
# import argparse
# import os
#
# import numpy as np
# import pandas as pd
#
# def main():
#     parser = argparse.ArgumentParser()
#     parser.add_argument('-d', '--data-directory')
#     args = parser.parse_args()
#
#     data_path = os.path.join(args.data_directory, 'profiling')
#     method_file = lambda bench, batch: os.path.join(data_path, bench, str(batch), 'summary', 'method.csv')
#
#     benchs = np.sort(os.listdir(data_path))
#
#     summary = []
#     for bench in benchs:
#         idx = ('benchmark', 'batches', 'correlation', 'correlation_err', 'correlation_rms')
#
#         batches = np.sort(os.listdir(os.path.join(data_path, bench)))
#         ranking = pd.concat([pd.read_csv(method_file(bench, batch)).assign(batch = int(batch)) for batch in batches])
#
#         ranking['method'] = ranking.trace.str.split(';').str[0]
#         ranking = ranking.groupby(['method', 'batch']).energy.sum()
#         ranking = ranking.reset_index()
#
#         df = pd.concat([
#             ranking[ranking.batch < len(batches)].assign(g = 0),
#             ranking.assign(g = 1)
#         ])
#         df = df.groupby(['method', 'g']).energy.sum()
#         df = df.unstack()
#         df = df / df.sum()
#
#         corr = df.corr().loc[0, 1]
#         corr_err = np.sqrt((1 - corr ** 2) / (len(df) - 2))
#
#         rms = (df[0] - df[1]) ** 2 / len(df)
#         rms = np.sqrt(rms.sum())
#
#         summary.append(pd.Series(
#             index = idx,
#             data = [bench, n, corr, corr_err, rms]
#         ))
#
#     summary_path = os.path.join(args.data_directory, 'summary')
#     if not os.path.exists(summary_path):
#         os.mkdir(summary_path)
#
#     df = pd.concat(summary, axis = 1).T.set_index(['benchmark', 'batches'])
#     df.to_csv(os.path.join(summary_path, 'convergence.csv'))
#     print(df)
#
# if __name__ == '__main__':
#     main()
