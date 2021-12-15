import math

import decimal
import datetime
import pandas as pd
import FinanceDataReader as fdr

pool = 20000
cnt = 0 # 수량
v = 0
week = 0
tqqq_amt = 0 # 평가금
min_v = 0
max_v = 0

def get_next_inc_rate():
    pool_div_v = decimal.Decimal(pool) / decimal.Decimal(v)
    amt_diff_v = tqqq_amt >= v
    amt_diff_v_2 = tqqq_amt < v

    if (pool_div_v >= 0.55 and amt_diff_v):
        return round(decimal.Decimal(1.06), 2)
    elif (pool_div_v >= decimal.Decimal(0.5) and amt_diff_v) or (pool_div_v >= decimal.Decimal(0.55) and amt_diff_v_2):
        return round(decimal.Decimal(1.055), 3)
    elif (pool_div_v >= decimal.Decimal(0.45) and amt_diff_v) or (pool_div_v >= decimal.Decimal(0.5) and amt_diff_v_2):
        return round(decimal.Decimal(1.05), 2)
    elif (pool_div_v >= decimal.Decimal(0.4) and amt_diff_v) or (pool_div_v >= decimal.Decimal(0.45) and amt_diff_v_2):
        return round(decimal.Decimal(1.045), 3)
    elif (pool_div_v >= decimal.Decimal(0.35) and amt_diff_v) or (pool_div_v >= decimal.Decimal(0.4) and amt_diff_v_2):
        return round(decimal.Decimal(1.04), 2)
    elif (pool_div_v >= decimal.Decimal(0.3) and amt_diff_v) or (pool_div_v >= decimal.Decimal(0.35) and amt_diff_v_2):
        return round(decimal.Decimal(1.035), 3)
    elif (pool_div_v >= decimal.Decimal(0.25) and amt_diff_v) or (pool_div_v >= decimal.Decimal(0.3) and amt_diff_v_2):
        return round(decimal.Decimal(1.03), 2)
    elif (pool_div_v >= decimal.Decimal(0.2) and amt_diff_v) or (pool_div_v >= decimal.Decimal(0.25) and amt_diff_v_2):
        return round(decimal.Decimal(1.025), 3)
    elif (pool_div_v >= decimal.Decimal(0.15) and amt_diff_v) or (pool_div_v >= decimal.Decimal(0.2) and amt_diff_v_2):
        return round(decimal.Decimal(1.02), 2)
    elif (pool_div_v >= decimal.Decimal(0.1) and amt_diff_v) or (pool_div_v >= decimal.Decimal(0.15) and amt_diff_v_2):
        return round(decimal.Decimal(1.015), 3)
    elif (pool_div_v >= decimal.Decimal(0.05) and amt_diff_v) or (pool_div_v >= decimal.Decimal(0.1) and amt_diff_v_2):
        return round(decimal.Decimal(1.01), 2)
    elif (pool_div_v >= decimal.Decimal(0.01) and amt_diff_v) or (pool_div_v >= decimal.Decimal(0.05) and amt_diff_v_2):
        return round(decimal.Decimal(1.005), 3)
    else:
        return round(decimal.Decimal(1.001), 3)

# 거치식 VR
if __name__ == '__main__':
    target = 'TQQQ'
    start_date = datetime.datetime(2018, 1, 1)
    # end_date = datetime.datetime.now()
    end_date = datetime.datetime(2018,12,31)
    df = fdr.DataReader(symbol='TQQQ', start=start_date, end=end_date)
    df_close_list = df['Close'].values  # 종가
    df_date = pd.to_datetime(df.index, format="%Y-%m-%d")

    for i in range(len(df)):
        close_price = round(decimal.Decimal(df_close_list[i]), 2) # 종가
        print('날짜 : {}, 종가 : {}'.format(df_date[i].strftime("%Y%m%d"), close_price))
        if (i % 10) == 0:
            print('rebalance')
            print('{}주차'.format(week))
            if week == 0:
                v = pool
                cnt = math.floor(pool / close_price)  # 수량
                pool -= round(decimal.Decimal(close_price * cnt), 2)
                inc_rate = get_next_inc_rate()
                print('상승률 : {}'.format(inc_rate))
            else:
                inc_rate = get_next_inc_rate()
                print('상승률 : {}'.format(inc_rate))
                v = round((v * inc_rate), 2)

            min_v = round((v * decimal.Decimal(0.8)), 2)
            max_v = round((v * decimal.Decimal(1.25)), 2)
            print('v : {}, min_v : {}, max_v : {}'.format(v, min_v, max_v))
            week += 2

        tqqq_amt = round((close_price * cnt), 2)  # 평가금
        print('tqqq수량 : {}, pool : {}, 평가금 : {}'.format(cnt, pool, tqqq_amt))

        if tqqq_amt < min_v: # 최소v보다 작을 경우
            rebl_buy_amt = (pool / decimal.Decimal(2)) if (min_v - tqqq_amt) > (pool / decimal.Decimal(2)) else (min_v - tqqq_amt) # rebalancing 금액(반절 넘지 않게)
            rebl_buy_cnt = math.ceil(rebl_buy_amt / close_price) # rebalancing용 매수 갯수
            print(rebl_buy_amt, rebl_buy_cnt)
            if rebl_buy_cnt > 0 and rebl_buy_amt >= close_price:
                print('@@@@@@@@@@@@@@@@@ rebalance 매수 @@@@@@@@@@@@@@@@@')
                pool -= round(rebl_buy_amt, 2)
                cnt += rebl_buy_cnt
            print('tqqq수량 : {}, pool : {}, 평가금 : {}'.format(cnt, pool, round((close_price * cnt), 2)))

        if tqqq_amt > max_v and pool < (v * decimal.Decimal(0.6)): # 최대v보다 크고 pool이 v*0.6보다 작을 경우
            rebl_sel_amt = (tqqq_amt - max_v) if (tqqq_amt - max_v + pool) < (v * decimal.Decimal(0.6)) else (v * decimal.Decimal(0.6)) - pool
            rebl_sel_cnt = math.ceil(rebl_sel_amt / close_price) # rebalancing용 매도 갯수
            print(rebl_sel_amt, rebl_sel_cnt)
            if rebl_sel_cnt > 0:
                print('@@@@@@@@@@@@@@@@@ rebalance 매도 @@@@@@@@@@@@@@@@@')
                pool += round(rebl_sel_amt, 2)
                cnt -= rebl_sel_cnt
            print('tqqq수량 : {}, pool : {}, 평가금 : {}'.format(cnt, pool, round((close_price * cnt), 2)))
