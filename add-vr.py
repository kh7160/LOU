import math

import yfinance as yf
import datetime
import pandas as pd

pool = 5000
cnt = 0 # 수량
v = 0
week = 0
tqqq_amt = 0 # 평가금
sell_loc_list = []
buy_loc_list = []

def get_next_inc_rate():
    if ((pool / v) >= 0.55 and (tqqq_amt >= v)):
        return 1.06
    elif ((pool / v) >= 0.5 and (tqqq_amt >= v)) or ((pool / v) >= 0.55 and (tqqq_amt < v)):
        return 1.055
    elif ((pool / v) >= 0.45 and (tqqq_amt >= v)) or ((pool / v) >= 0.5 and (tqqq_amt < v)):
        return 1.05
    elif ((pool / v) >= 0.4 and (tqqq_amt >= v)) or ((pool / v) >= 0.45 and (tqqq_amt < v)):
        return 1.045
    elif ((pool / v) >= 0.35 and (tqqq_amt >= v)) or ((pool / v) >= 0.4 and (tqqq_amt < v)):
        return 1.04
    elif ((pool / v) >= 0.3 and (tqqq_amt >= v)) or ((pool / v) >= 0.35 and (tqqq_amt < v)):
        return 1.035
    elif ((pool / v) >= 0.25 and (tqqq_amt >= v)) or ((pool / v) >= 0.3 and (tqqq_amt < v)):
        return 1.03
    elif ((pool / v) >= 0.2 and (tqqq_amt >= v)) or ((pool / v) >= 0.25 and (tqqq_amt < v)):
        return 1.025
    elif ((pool / v) >= 0.15 and (tqqq_amt >= v)) or ((pool / v) >= 0.2 and (tqqq_amt < v)):
        return 1.02
    elif ((pool / v) >= 0.1 and (tqqq_amt >= v)) or ((pool / v) >= 0.15 and (tqqq_amt < v)):
        return 1.015
    elif ((pool / v) >= 0.05 and (tqqq_amt >= v)) or ((pool / v) >= 0.1 and (tqqq_amt < v)):
        return 1.01
    elif ((pool / v) >= 0.01 and (tqqq_amt >= v)) or ((pool / v) >= 0.05 and (tqqq_amt < v)):
        return 1.005
    else:
        return 1.001

# 적립식 VR
if __name__ == '__main__':
    target = 'TQQQ'
    add_pool = 250
    start_date = datetime.datetime(2021, 7, 16)
    end_date = datetime.datetime.now()
    df = yf.download(target, start=start_date, end=end_date)
    df_close_list = df['Close'].values  # 종가
    df_date = pd.to_datetime(df.index, format="%Y-%m-%d")
    v = pool
    cnt = math.floor(pool / df_close_list[0]) # 수량
    tqqq_amt = round((df_close_list[0] * cnt), 4) # 평가금
    pool = round((pool - tqqq_amt), 4)
    # 실제 구매 데이터TEST
    v = 6692.64
    cnt = 52
    pool = 1093.72
    tqqq_amt = round((df_close_list[0] * cnt), 4)  # 평가금
    ######################################################
    inc_rate = get_next_inc_rate()
    print('상승률 : {}'.format(inc_rate))
    pool += add_pool
    v = round((v * inc_rate), 2) + add_pool
    min_v = round((v * 0.8), 2)
    max_v = round((v * 1.25), 2)
    for j in range(14):  # rebalance day에 loc 매수, 매도 가격 계산
        buy_loc_list.append(round(min_v / (cnt + j), 2))
        sell_loc_list.append(round(max_v / (cnt - j), 2))
    print('매수loc : {}\n매도loc : {}'.format(buy_loc_list, sell_loc_list))

    print('tqqq수량 : {}, pool : {}, 평가금 : {}'.format(cnt, pool, tqqq_amt))
    print('v : {}, min_v : {}, max_v : {}'.format(v, min_v, max_v))

    for i in range(1, len(df)):
        close_price = round(df_close_list[i], 4) # 종가
        print('날짜 : {}, 종가 : {}'.format(df_date[i].strftime("%Y%m%d"), close_price))
        tqqq_amt = round((close_price * cnt), 4)  # 평가금
        print('tqqq수량 : {}, pool : {}, 평가금 : {}'.format(cnt, pool, tqqq_amt))
        if (i % 10) == 0:
            week += 2
            print('{}주차'.format(week))
            pool += add_pool
            buy_loc_list.clear()
            sell_loc_list.clear()
            print('rebalance day')
            inc_rate = get_next_inc_rate()
            print('상승률 : {}'.format(inc_rate))
            v = round((v * inc_rate), 2) + add_pool
            min_v = round((v * 0.8), 2)
            max_v = round((v * 1.25), 2)
            tqqq_amt = round((close_price * cnt), 4)  # 평가금
            print('tqqq수량 : {}, pool : {}, 평가금 : {}'.format(cnt, pool, tqqq_amt))
            print('v : {}, min_v : {}, max_v : {}'.format(v, min_v, max_v))

            for j in range(14): # rebalance day에 loc 매수, 매도 가격 계산
                buy_loc_list.append(round(min_v / (cnt + j), 2))
                sell_loc_list.append(round(max_v / (cnt - j), 2))
            print('매수loc : {}\n매도loc : {}'.format(buy_loc_list, sell_loc_list))

        if (close_price < buy_loc_list[0]) and (pool >= close_price): # 종가 < 매수가격 and pool >= 종가 : 1주 매수
            print('@@@@@@@@@@@@@@@@@@@ 종가({}) < 매수가격({}) and pool >= 종가 @@@@@@@@@@@@@@@@@@@'.format(close_price, buy_loc_list[0]))
            cnt += 1
            pool = round((pool - close_price), 4)
            tqqq_amt = round((close_price * cnt), 4)  # 평가금
            buy_loc_list.pop(0)
            # print('tqqq수량 : {}, pool : {}, 평가금 : {}'.format(cnt, pool, tqqq_amt))

        if (close_price > sell_loc_list[0]) and (pool < (v * 0.6)): # 종가 > 매도가격 and pool < v*0.6 : 1주 매수
            print('@@@@@@@@@@@@@@@@@@@ 종가({}) > 매도가격({}) and pool < v*0.6 @@@@@@@@@@@@@@@@@@@'.format(close_price, sell_loc_list[0]))
            cnt -= 1
            pool = round((pool + close_price), 4)
            tqqq_amt = round((close_price * cnt), 4)  # 평가금
            sell_loc_list.pop(0)
            # print('tqqq수량 : {}, pool : {}, 평가금 : {}'.format(cnt, pool, tqqq_amt))