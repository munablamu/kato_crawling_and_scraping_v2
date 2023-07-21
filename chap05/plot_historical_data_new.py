from datetime import datetime

import pandas as pd
import matplotlib
matplotlib.use('Agg')
matplotlib.rcParams['font.sans-serif'] = 'MigMix 1P'
import matplotlib.pyplot as plt


def main():
    # 為替データの読み込み。
    df_exchange = pd.read_csv(
        'exchange.csv', encoding='cp932', header=1, names=['date', 'USD', 'rate'],
        index_col=0, parse_dates=True
    )
    # 国債金利データの読み込み。
    df_jgbcm = pd.read_csv(
        'jgbcm_all.csv', encoding='cp932', header=1, index_col=0, parse_dates=True,
        date_parser=parse_japanese_date, na_values=['-']
    )
    # 新様式の有効求人倍率データの読み込み。
    df_jobs = pd.read_excel('第3表(新様式).xlsx', skiprows=3, skipfooter=3, usecols='A,U:AF', index_col=0)
    # pandas 0.24以降では列ラベルに.1のような接頭辞がつくので、接頭辞がある場合は取り除く。
    df_jobs.columns = [c.split('.')[0] for c in df_jobs.columns]
    df_jobs = df_jobs.drop(df_jobs.index[0]) # 1行目を削除
    s_jobs = df_jobs.stack()
    s_jobs.index = [parse_year_and_month(y, m) for y, m in s_jobs.index]

    min_date = datetime(1973, 1, 1)
    max_date = datetime.now()

    # 1つ目のサブプロット（為替データ）
    plt.subplot(3, 1, 1)
    plt.plot(df_exchange.index, df_exchange.USD, label='ドル・円')
    plt.xlim(min_date, max_date)
    plt.ylim(50, 250)
    plt.legend(loc='best')
    # 2つ目のサブプロット（国債金利データ）
    plt.subplot(3, 1, 2)
    plt.plot(df_jgbcm.index, df_jgbcm['1年'], label='1年国債金利')
    plt.plot(df_jgbcm.index, df_jgbcm['5年'], label='5年国債金利')
    plt.plot(df_jgbcm.index, df_jgbcm['10年'], label='10年国債金利')
    plt.xlim(min_date, max_date)
    plt.legend(loc='best')
    # 3つ目のサブプロット（有効求人倍率データ）
    plt.subplot(3, 1, 3)
    plt.plot(s_jobs.index, s_jobs, label='有効求人倍率(季節調整値)')
    plt.xlim(min_date, max_date)
    plt.ylim(0.0, 2.0)
    plt.axhline(y=1, color='gray') # y=1の水平線を引く。
    plt.legend(loc='best')

    plt.savefig('historical_data_new.png', dpi=300)


def parse_japanese_date(s: str) -> datetime:
    """
    'H30.8.31'のような和暦の日付をdatetimeオブジェクトに変換する。
    """
    base_years = {'S': 1925, 'H': 1988, 'R': 2018}
    era = s[0]
    year, month, day = s[1:].split('.')
    year = base_years[era] + int(year)
    return datetime(year, int(month), int(day))


def parse_year_and_month(year: str, month: str) -> datetime:
    """
    ('X年', 'Y月')の組をdatetimeオブジェクトに変換する。
    """
    year = int(year[:-1])
    month = int(month[:-1])
    return datetime(year, month, 1)


if __name__ == '__main__':
    main()
