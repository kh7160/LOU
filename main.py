import math

import yfinance as yf
import telegram
import datetime

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

total_ca = 6000 # 총예수금
init_ca = 6000 # 초기 예수금 기준
ca_per_day = math.floor(init_ca / 40) # 하루예수금
avg_buy_cost = 0 # 평단
total_buy_amt = 0 # 총매입금액
total_buy_cnt = 0 # 총매입수량
total_cnt = 0 # 회차
profit_amt = 0 # 총이익금
sell_cnt = 0 # 매도회수
cnt_40 = 0 # 40 초과 회수

def RSI(target, end, window=14, adjust=False):
    data = yf.download(target, end=end)  # High(고가), Close(종가)
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

def sendTelegram():
    token = "5086537703:AAEC6pdIaNxWZi8nwJrjEAWjy6S_6h1mt0w"
    bot = telegram.Bot(token)
    keys = list(const_LOU_dict.keys())
    message = "{} : {} / {} / {}({})\n"
    final_message = "현재 RSI / 권장 RSI / 가능유무\n"
    for i in range(len(keys)):
        df = yf.download(keys[i])
        rsi = round(RSI(df), 2)
        final_message += message.format(keys[i], rsi[-1], const_LOU_dict[keys[i]], "가능" if rsi[-1] < const_LOU_dict[keys[i]] else "불가능", round(const_LOU_dict[keys[i]] - rsi[-1]), 2)

    bot.sendMessage(chat_id=bot.getUpdates()[0].message.chat_id, text=final_message)

if __name__ == '__main__':
    target = 'FNGU'
    # df = yf.download(test_target, datetime(2021,12,1), datetime.now()) # High(고가), Close(종가)
    df = yf.download(target, datetime.datetime(2021,1,1), datetime.datetime(2021,12,4)) # High(고가), Close(종가)
    rsi_end_date = datetime.datetime(2020,12,31) # RSI용 end_date
    close_price_df = df['Close'].values  # 종가
    high_price_df = df['High'].values  # 고가

    for i in range(len(df)):
        close_price = round(close_price_df[i], 4)
        high_price = round(high_price_df[i], 4)
        rsi_end_date = rsi_end_date + datetime.timedelta(days=1)
        buy_able_cnt = math.floor(ca_per_day / close_price)  # 매수 가능 숫자(loc 주문이어서 종가 기준)
        loc_avg_cnt = math.ceil(buy_able_cnt / 2) # loc평단매수개수
        loc_high_cnt = buy_able_cnt - loc_avg_cnt # loc큰수매수개수
        avg_buy_cost = 0 if total_buy_cnt == 0 else round(total_buy_amt / total_buy_cnt, 4) # 평단가
        sell_goal_cost = round(avg_buy_cost * 1.1, 4) # 매도가격(10%)
        print("\n종가 : {}, 고가 : {}, 매수가능개수 : {}, loc평단매수개수 : {}, loc큰수매수개수 : {}, 평단가 : {}, 매도가격 : {}".format(close_price, high_price, buy_able_cnt, loc_avg_cnt, loc_high_cnt, avg_buy_cost, sell_goal_cost))

        if total_cnt == 0: # 첫회는 무조건 매수
            print('================== 첫회는 무조건 매수 ==================')
            rsi = round(RSI(target, rsi_end_date), 2)
            if rsi[-1] > const_LOU_dict[target]:
                print('권장 RSI를 초과하기 때문에 매수를 추천하지 않습니다.')
                print('날짜 : {}, rsi : {}, 권장 rsi : {}'.format(rsi_end_date, rsi[-1], const_LOU_dict[target]))
                continue

            day_buy_amt = round(buy_able_cnt * close_price, 4)
            total_buy_amt += day_buy_amt
            total_buy_cnt += buy_able_cnt
            total_ca -= day_buy_amt  # 예수금 계산
            total_cnt += 1  # 회차 추가
            print("회차 : {}, 총매수금액 : {}, 총매수개수 : {}, 총예수금 : {}".format(total_cnt, total_buy_amt, total_buy_cnt, round(total_ca, 4)))
            continue

        if total_cnt == 40:
            print('※※※※※※※※※※※※※※ 40회 소진 발생 ※※※※※※※※※※※※※※')

        if high_price >= sell_goal_cost: # 고가 > 평단가 * 1.1
            print('@@@@@@@@@@@@@@@@@@ 매도 발생(고가>평단가 * 1.1) @@@@@@@@@@@@@@@@@@')
            day_sel_amt = round(sell_goal_cost * total_buy_cnt, 4) # 매도단가 * 총개수
            profit_amt += (day_sel_amt - total_buy_amt)  # 총이익금
            total_buy_amt = 0 # 0 리셋
            total_buy_cnt = 0 # 0 리셋
            total_ca += day_sel_amt # 예수금 계산
            sell_cnt += 1
            total_cnt = 0 # 회차 리셋
            print("회차 : {}, 매도금액 : {}, 총매수금액 : {}, 총매수개수 : {}, 총예수금 : {}\n".format(total_cnt, day_sel_amt, total_buy_amt, total_buy_cnt, round(total_ca, 4)))

        if close_price <= avg_buy_cost : # 종가 <= 평단가(loc평단매수시 매수 조건)
            print('================== loc 평단매수 발생(종가>평단가) ==================')
            day_buy_amt = round(loc_avg_cnt * close_price, 4) # 당일 매수
            total_buy_amt += day_buy_amt # 총매수금액 계산
            total_buy_cnt += loc_avg_cnt # 총매수개수 계산
            total_ca -= day_buy_amt # 예수금 계산
            total_cnt += 0.5 # 회차 계산
            print("회차 : {}, 매수금액 : {}, 총매수금액 : {}, 총매수개수 : {}, 총예수금 : {}".format(total_cnt, day_buy_amt, total_buy_amt, total_buy_cnt, round(total_ca, 4)))

        if close_price <= avg_buy_cost * 1.1: # 종가 <= 평단가 * 1.1
            print('================== loc 큰수매수 발생(종가 < 평단가 * 1.1) ==================')
            day_buy_amt = round(loc_high_cnt * close_price, 4)
            total_buy_amt += day_buy_amt # 총매수금액 계산
            total_buy_cnt += loc_high_cnt # 총매수개수 계산
            total_ca -= day_buy_amt # 예수금 계산
            total_cnt += 0.5 # 회차 계산
            print("회차 : {}, 매수금액 : {}, 총매수금액 : {}, 총매수개수 : {}, 총예수금 : {}".format(total_cnt, day_buy_amt, total_buy_amt, total_buy_cnt, round(total_ca, 4)))

    print('총이익금 : {}, 매도횟수 : {}'.format(profit_amt, sell_cnt))