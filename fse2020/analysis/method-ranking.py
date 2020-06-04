#!/usr/bin/python3

import argparse
import os

from itertools import product
from time import time

import matplotlib
matplotlib.use('Agg')

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns

from tqdm import tqdm

def ranking_plot(df, colors):
    df.index = df.index.str.replace('$', '\$')

    ax = df.tail(10).plot.barh(
        width = 0.33,
        legend = False,
        align = 'edge',
        color = colors,
        figsize = (16, 9)
    )

    ax.spines['right'].set_visible(False)
    ax.spines['top'].set_visible(False)

    for rect, name in zip(ax.patches, df.tail(10).index):
        height = rect.get_height()
        ax.text(
            df.max().max() * 0.005,
            (rect.get_y() + height + 0.20) if len(df.columns) > 1 else (rect.get_y() + height + 0.05),
            name,
            ha='left', va='bottom', fontsize = 24
        )

    if isinstance(df, pd.DataFrame):
        handles, labels = ax.get_legend_handles_labels()
        ax.legend(handles[::-1], labels[::-1], loc = 'lower right', fontsize = 24)

    plt.xlim(0, ((5 * df.max().max()).astype(int) + 1) / 5)

    plt.xlabel('Normalized Energy Consumption', fontsize = 28)
    plt.ylabel(df.index.name.title(), fontsize = 28)

    plt.yticks([])
    plt.xticks(fontsize = 32)

    return ax.get_figure()

def get_n_contexts(df, n):
    context1 = df.trace.str.split(';').str[1].str.split('.').str[-2:].str.join('.')
    context2 = df.trace.str.split(';').str[2].str.split('.').str[-2:].str.join('.')
    context = df.copy(deep = True).assign(context = "[" + context1 + ", " + context2 + "]")

    top_methods = context.groupby('method_').energy.sum().sort_values(ascending = False).head(n).index.values

    context = context[context.method_.isin(top_methods)].groupby(['method_', 'context']).energy.sum().reset_index()
    context['method'] = context.method_.str.split('.').str[-2:].str.join('.')
    context = context.set_index(['method', 'context']).energy
    context /= context.groupby('method').sum()

    return context

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('-work-directory')
    args = parser.parse_args()

    data_path = args.work_directory
    plots_path = os.path.join(data_path, 'plots')
    if not os.path.exists(plots_path):
        os.mkdir(plots_path)

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
        runs = np.sort(os.listdir(os.path.join(calm_data, bench, 'raw')))
        runs = runs[(len(runs) // 5):]

        df = pd.concat([pd.read_csv(
            os.path.join(profile_data, bench, str(n), 'summary', 'method.csv')
        ).assign(batch = n) for n, k in product(os.listdir(os.path.join(profile_data, bench)), runs)])

        df['method_'] = df.trace.str.split(';').str[0]

        benchs_.set_description(bench + " - ranking")

        ranking = df.copy(deep = True).groupby('method_')[['energy', 'time']].sum()
        ranking.energy = ranking.energy / ranking.energy.sum()
        ranking.time = ranking.time / ranking.time.sum()

        ranking['method'] = ranking.index.str.split('.').str[-2:].str.join('.')
        ranking_plot(ranking.set_index('method').sort_values(by = ['energy'])[['time', 'energy']], colors = [u'#d62728', u'#2ca02c'])
        plt.savefig(os.path.join(plots_path, bench, 'method-ranking.pdf'.format(bench)), bbox_inches = 'tight')
        plt.close()

        ranking['method'] = ranking.index.str.split('.').str[-2:].str.join('.')
        ranking_plot(ranking.set_index('method')[['energy']].sort_values(by = ['energy']), colors = u'#2ca02c')
        plt.savefig(os.path.join(plots_path, bench, 'energy-method-ranking.pdf'.format(bench)), bbox_inches = 'tight')
        plt.close()

        ranking['class'] = ranking.index.str.split('.').str[-2]
        ranking_plot(ranking.groupby('class')[['energy']].sum().sort_values(by = ['energy']), colors = u'#2ca02c')
        plt.savefig(os.path.join(plots_path, bench, 'class-ranking.pdf'.format(bench)), bbox_inches = 'tight')
        plt.close()

        ranking['package'] = ranking.index.str.split('.').str[:-2].str.join('.')
        ranking_plot(ranking.groupby('package')[['energy']].sum().sort_values(by = ['energy']), colors = u'#2ca02c')
        plt.savefig(os.path.join(plots_path, bench, 'package-ranking.pdf'.format(bench)), bbox_inches = 'tight')
        plt.close()

        benchs_.set_description(bench + " - context")

        context = get_n_contexts(df, 3)

        for i, (method, df) in enumerate(context.groupby('method')):
            ax = df.plot.pie(
                x = 'context', y = 'energy',
                labels = None,
                wedgeprops = {'edgecolor': 'k', 'linewidth': 1},
                figsize = (24, 16)
            )

            plt.title(method, fontsize = 72)
            plt.xlabel('')
            plt.ylabel('')

            context = df.index.get_level_values(1)
            if len(df) < 15:
                ax.legend(context, loc = 'upper left', bbox_to_anchor = (0.925, 0.925), frameon = False, fontsize = 48)
            else:
                ax.legend(context, fontsize = 10, ncol = int(np.ceil(len(df) / 30)))

            plt.savefig(os.path.join(plots_path, bench, 'cfa2_{}.pdf'.format(i + 1)), bbox_inches = 'tight')
            plt.close()

if __name__ == '__main__':
    main()
