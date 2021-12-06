import yfinance as yf
import telegram

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

def RSI(data, window=14, adjust=False):
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

def connectTelegram():
    token = "5086537703:AAEC6pdIaNxWZi8nwJrjEAWjy6S_6h1mt0w"
    bot = telegram.Bot(token)
    # bot.sendMessage(chat_id=bot.getUpdates()[0].message.chat_id, text="")
    return bot

if __name__ == '__main__':
    bot = connectTelegram()
    keys = list(const_LOU_dict.keys())
    message = "{} : {} / {} / {}({})\n"
    final_message = "현재 RSI / 권장 RSI / 가능유무\n"
    for i in range(len(keys)):
        lvg_etf = yf.download(keys[i])
        rsi = round(RSI(lvg_etf), 2)
        final_message += message.format(keys[i], rsi[-1], const_LOU_dict[keys[i]], "가능" if rsi[-1] < const_LOU_dict[keys[i]] else "불가능", round(const_LOU_dict[keys[i]] - rsi[-1]), 2)

    # print(final_message)
    bot.sendMessage(chat_id=bot.getUpdates()[0].message.chat_id, text=final_message)