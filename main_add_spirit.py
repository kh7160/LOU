import math

import yfinance as yf
import telegram
import datetime
import pandas as pd

# 라오어 추천 ETF
const_LOU_dict = {
     'BULZ':65  # 기술
    ,'SOXL':65  # 기술
    ,'TQQQ':60  # 기술
    ,'TECL':60  # 기술
    ,'FNGU':55  # 기술
    ,'UPRO':55  # S&P500
    ,'TNA':50   # 중소형주
    ,'UDOW':50  # 다우
    ,'FAS':45   # 금융
    ,'LABU':45  # 바이오
    ,'DFEN':40  # 항공/방산
    ,'DPST':35  # 금융
}

total_ca = 12000 # 총예수금
init_ca = 6000 # 초기 예수금 기준
current_acno = 1 # 현재 사용 계좌번호

init_dict = \
    {
        'ca_per_day':math.floor(init_ca/40)
        ,'avg_buy_cost':0
        ,'total_buy_amt':0
        ,'total_buy_cnt':0
        ,'total_cnt':0
        ,'profit_amt':0
        ,'sell_cnt':0
        ,'cnt_40':0
        ,'profit_rate':0
   }

acno_dict = {
    current_acno:init_dict
}

def RSI(df, end_date, window=14, adjust=False):
    print('***************** RSI ****************')
    data = df[:end_date]
    delta = data['Adj Close'].diff(1).dropna()
    loss = delta.copy()
    gains = delta.copy()

    gains[gains < 0] = 0
    loss[loss > 0] = 0

    gain_ewm = gains.ewm(com=window - 1, adjust=adjust).mean()
    loss_ewm = abs(loss.ewm(com=window - 1, adjust=adjust).mean())

    RS = gain_ewm / loss_ewm
    RSI = 100 - 100 / (1 + RS)

    return RSI

if __name__ == '__main__':
    target = 'LABU'
    rsi_df = yf.download(target, end=datetime.datetime.now()) # rsi용 데이터 전체 다운로드
    first_date = pd.to_datetime(rsi_df.index, format="%Y-%m-%d, %H:%M:%S")[0]
    start_date = datetime.datetime(2021,2,1)
    end_date = datetime.datetime.now()
    # end_date = datetime.datetime(2021,6,28)
    # df = rsi_df[first_date:end_date] # 테스트 기간용 데이터
    df = rsi_df[start_date:end_date] # 테스트 기간용 데이터
    df['Datetime'] = pd.to_datetime(df.index, format="%Y-%m-%d, %H:%M:%S")
    close_price_df = df['Close'].values  # 종가
    high_price_df = df['High'].values  # 고가

    for i in range(len(df)):
        close_price = round(close_price_df[i], 4) # 종가
        high_price = round(high_price_df[i], 4) # 고가
        rsi_end_date = df['Datetime'][i] # 매수용 RSI 계산날짜
        buy_able_cnt = math.floor(acno_dict[current_acno]['ca_per_day'] / close_price)  # 매수 가능 숫자(loc 주문이어서 종가 기준)
        loc_avg_cnt = math.ceil(buy_able_cnt / 2) # loc평단매수개수
        loc_high_cnt = buy_able_cnt - loc_avg_cnt # loc큰수매수개수
        acno_dict[current_acno]['avg_buy_cost'] = 0 if acno_dict[current_acno]['total_buy_cnt'] == 0 else round(acno_dict[current_acno]['total_buy_amt'] / acno_dict[current_acno]['total_buy_cnt'], 4) # 평단가
        sell_goal_cost = round(acno_dict[current_acno]['avg_buy_cost'] * 1.1, 2) # 매도가격(10%)
        print("\n종가 : {}, 고가 : {}, 매수가능개수 : {}, loc평단매수개수 : {}, loc큰수매수개수 : {}, 평단가 : {}, 매도가격 : {}".format(close_price, high_price, buy_able_cnt, loc_avg_cnt, loc_high_cnt, acno_dict[current_acno]['avg_buy_cost'], sell_goal_cost))

        if acno_dict[current_acno]['total_cnt'] == 0: # 첫회는 무조건 매수
            print('================== 첫회는 무조건 매수 ==================')
            rsi = round(RSI(rsi_df, rsi_end_date), 2) # 매수용 RSI 계산
            if (rsi.empty): # 첫상장날의 경우 rsi계산 불가
                continue

            if rsi[-1] > const_LOU_dict[target]:
                print('권장 RSI를 초과하기 때문에 매수를 추천하지 않습니다.')
                print('날짜 : {}, rsi : {}, 권장 rsi : {}'.format(rsi_end_date, rsi[-1], const_LOU_dict[target]))
                continue

            day_buy_amt = round(buy_able_cnt * close_price, 4)
            acno_dict[current_acno]['total_buy_amt'] += day_buy_amt
            acno_dict[current_acno]['total_buy_cnt'] += buy_able_cnt
            total_ca -= day_buy_amt  # 예수금 계산
            acno_dict[current_acno]['total_cnt'] += 1  # 회차 추가
            print("회차 : {}, 총매수금액 : {}, 총매수개수 : {}, 총예수금 : {}".format(acno_dict[current_acno]['total_cnt'], acno_dict[current_acno]['total_buy_amt'], acno_dict[current_acno]['total_buy_cnt'], round(total_ca, 4)))
            continue

        if acno_dict[current_acno]['total_cnt'] == 40:
            print('※※※※※※※※※※※※※※ 40회 소진 발생 ※※※※※※※※※※※※※※')

            profit_rate = round((close_price - acno_dict[current_acno]['avg_buy_cost']) / acno_dict[current_acno]['avg_buy_cost'], 2)
            print(profit_rate)
            if profit_rate >= -0.01: # 수익률 -10% 이상일 경우 손절
                print('※※※※※※※※※※※※※※ 수익률 -10이상일 경우 손절 ※※※※※※※※※※※※※※')
                day_sel_amt = round(close_price * acno_dict[current_acno]['total_buy_cnt'], 4)  # 종가 * 총개수
                total_ca += day_sel_amt # 예수금 계산
                print("회차 : {}, 매도금액 : {}, 총매수금액 : {}, 총매수개수 : {}, 총예수금 : {}\n".format(acno_dict[current_acno]['total_cnt'], day_sel_amt,
                                                                                       acno_dict[current_acno]['total_buy_amt'], acno_dict[current_acno]['total_buy_cnt'],
                                                                                       round(total_ca, 4)))
                acno_dict[current_acno]['total_buy_amt'] = 0 # 0 리셋
                acno_dict[current_acno]['total_buy_cnt'] = 0 # 0 리셋
                acno_dict[current_acno]['total_cnt'] = 0 # 회차 리셋
                acno_dict[current_acno]['sell_cnt'] += 1  # 매도 횟수
                acno_dict[current_acno]['cnt_40'] += 1 # 40회 소진 횟수
            else: # 수익률 -10% 이하일 경우 영혼법
                if total_ca > init_ca:
                    print('※※※※※※※※※※※※※※ 영혼법 발생 ※※※※※※※※※※※※※※')
                    current_acno += 1
                    acno_dict[current_acno] = init_dict
                    print(acno_dict)
                    continue
                else:
                    print('※※※※※※※※※※※※※※ 예수금 부족 ※※※※※※※※※※※※※※')
                    exit(-1)

        if high_price >= sell_goal_cost: # 고가 > 평단가 * 1.1
            print('@@@@@@@@@@@@@@@@@@ 매도 발생(고가>평단가 * 1.1) @@@@@@@@@@@@@@@@@@')
            day_sel_amt = round(sell_goal_cost * acno_dict[current_acno]['total_buy_cnt'], 4) # 매도단가 * 총개수
            acno_dict[current_acno]['profit_amt'] += (day_sel_amt - acno_dict[current_acno]['total_buy_amt'])  # 총이익금
            total_ca += day_sel_amt # 예수금 계산
            acno_dict[current_acno]['profit_rate'] = round(acno_dict[current_acno]['profit_amt']/init_ca, 2) # 이익률 계산
            print("회차 : {}, 매도금액 : {}, 총매수금액 : {}, 총매수개수 : {}, 총예수금 : {}\n".format(acno_dict[current_acno]['total_cnt'], day_sel_amt, acno_dict[current_acno]['total_buy_amt'], acno_dict[current_acno]['total_buy_cnt'], round(total_ca, 4)))
            acno_dict[current_acno]['total_buy_amt'] = 0 # 0 리셋
            acno_dict[current_acno]['total_buy_cnt'] = 0 # 0 리셋
            acno_dict[current_acno]['sell_cnt'] += 1 # 매도 횟수
            acno_dict[current_acno]['total_cnt'] = 0 # 회차 리셋

        if (close_price <= acno_dict[current_acno]['avg_buy_cost']) and loc_avg_cnt != 0: # 종가 <= 평단가(loc평단매수시 매수 조건)
            print('================== loc 평단매수 발생(종가 <= 평단가) ==================')
            day_buy_amt = round(loc_avg_cnt * close_price, 4) # 당일 매수
            acno_dict[current_acno]['total_buy_amt'] += day_buy_amt # 총매수금액 계산
            acno_dict[current_acno]['total_buy_cnt'] += loc_avg_cnt # 총매수개수 계산
            total_ca -= day_buy_amt # 예수금 계산
            acno_dict[current_acno]['total_cnt'] += 0.5 # 회차 계산
            print("회차 : {}, 매수금액 : {}, 총매수금액 : {}, 총매수개수 : {}, 총예수금 : {}".format(acno_dict[current_acno]['total_cnt'], day_buy_amt, acno_dict[current_acno]['total_buy_amt'], acno_dict[current_acno]['total_buy_cnt'], round(total_ca, 4)))

        if (close_price <= acno_dict[current_acno]['avg_buy_cost'] * 1.1) and loc_high_cnt != 0: # 종가 <= 평단가 * 1.1
            print('================== loc 큰수매수 발생(종가 <= 평단가 * 1.1) ==================')
            day_buy_amt = round(loc_high_cnt * close_price, 4)
            acno_dict[current_acno]['total_buy_amt'] += day_buy_amt # 총매수금액 계산
            acno_dict[current_acno]['total_buy_cnt'] += loc_high_cnt # 총매수개수 계산
            total_ca -= day_buy_amt # 예수금 계산
            acno_dict[current_acno]['total_cnt'] += 0.5 # 회차 계산
            print("회차 : {}, 매수금액 : {}, 총매수금액 : {}, 총매수개수 : {}, 총예수금 : {}".format(acno_dict[current_acno]['total_cnt'], day_buy_amt, acno_dict[current_acno]['total_buy_amt'], acno_dict[current_acno]['total_buy_cnt'], round(total_ca, 4)))

    print('총이익금 : {}, 매도횟수 : {}'.format(acno_dict[current_acno]['profit_amt'], acno_dict[current_acno]['sell_cnt']))