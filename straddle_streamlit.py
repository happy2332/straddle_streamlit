from datetime import datetime
import streamlit as st
from kiteconnect import KiteConnect
import time
import pytz
import logging
logging.basicConfig(level=logging.DEBUG)

IST = pytz.timezone('Asia/Kolkata')


def getCMP(kite, tradingSymbol):
    quote = kite.quote(tradingSymbol)
    if quote:
        return quote[tradingSymbol]['last_price']
    else:
        return 0

def getCMPLogLines(kite):
    current_time = datetime.now(IST).strftime("%H:%M:%S")
    result = f"Time : {current_time} ---> "
    #result += f"Banknifty: {getCMP(kite, 'NSE:NIFTY BANK')}, "
    #result += f"Nifty: {getCMP(kite, 'NSE:NIFTY 50')}"
    return result

def placeOrder(kite, symbol, qty=50):
    try:
        st.write(f"Placing order for {symbol} with {qty} quantity")
        order_id = kite.place_order(exchange=KiteConnect.EXCHANGE_NFO,
                                    tradingsymbol=symbol,
                                    transaction_type=kite.TRANSACTION_TYPE_SELL,
                                    quantity=qty,
                                    order_type = KiteConnect.ORDER_TYPE_MARKET, 
                                    variety = kite.VARIETY_REGULAR,
                                    product = KiteConnect.PRODUCT_MIS)
        st.write(f"Order successfully placed for {symbol} with {qty} quantity")
        return order_id
    except Exception as e:
        st.write(f'Order placement failed: {e}')

def tradingLoop(kite, trade_time, bnf_qty, nifty_qty):
    trade_hr, trade_min, trade_sec = trade_time.split(':')
    text = st.empty()
    lines = ""
    count = 0
    max_count = 12000
    log_print_steps = 10
    log_print_count = 0
    max_log_print = 15
    bnf_base = 100
    nifty_base = 50
    while True:
        if log_print_count == max_log_print:
            lines = ""
        if count == max_count:
            break
        if count%log_print_steps == 0:
            lines += getCMPLogLines(kite)+"\n"
            text.text_area(label = "Printing Logs", value = lines, height=300)
            log_print_count += 1
        current_time = datetime.now(IST).time()
        if current_time.hour == int(trade_hr) and current_time.minute == int(trade_min) and current_time.second > int(trade_sec):
            current_bnf_spot = getCMP(kite,'NSE:NIFTY BANK')
            current_nifty_spot = getCMP(kite, 'NSE:NIFTY 50')
            if bnf_qty > 0:
                atm_price = bnf_base * round(current_bnf_spot/bnf_base) 
                symbol = 'BANKNIFTY22113'+str(atm_price)+'PE'
                placeOrder(kite, symbol, qty=bnf_qty)
                symbol = 'BANKNIFTY22113'+str(atm_price)+'CE'
                placeOrder(kite, symbol, qty=bnf_qty)
            
            if nifty_qty > 0:
                atm_price = nifty_base * round(current_nifty_spot/nifty_base) 
                symbol = 'NIFTY22113'+str(atm_price)+'PE'
                placeOrder(kite, symbol, qty=nifty_qty)
                symbol = 'NIFTY22113'+str(atm_price)+'CE'
                placeOrder(kite, symbol, qty=nifty_qty)
            break
        time.sleep(1)
        count += 1


def main():
    st.title('Automated Intraday Straddle App')
    trade_time = st.sidebar.text_input('Enter trade time','10:55:00')    
    bnf_qty = 0
    nifty_qty = 0
    bnf_qty = int(st.sidebar.text_input('Enter Banknifty qty','0'))
    nifty_qty = int(st.sidebar.text_input('Enter Nifty qty','0'))
    api_key=st.secrets["api_key"]
    api_secret=st.secrets["api_secret"]
    st.write("Click on this [link](https://kite.trade/connect/login?api_key="+api_key+"&v=3) for kite login.")
    request_token = st.text_input('Enter request_token:','')
    
    if st.button("Next"):
        if bnf_qty > 0 or nifty_qty > 0:   
            #api_key = "600whbxnxb8o616h"
            #api_secret = "evrckz4qfodc2n59b4nkawdksvwy2156"
            kite = KiteConnect(api_key=api_key)
            data = kite.generate_session(request_token,api_secret = api_secret)
            st.write("Congratulations !!! You are successfully authorized")
            # st.write(f"CMP for NIFTY : {getCMP(kite, 'NSE:NIFTY 50')}")
            # st.write(f"CMP for BANKNIFTY : {getCMP(kite, 'NSE:NIFTY BANK')}")
            st.write(f"Your trade will be taken at {trade_time} in Banknifty with {bnf_qty} qty and Nifty with {nifty_qty} qty!!!")
            tradingLoop(kite, trade_time, bnf_qty, nifty_qty)
        # except:
        #     st.write("Sorry, connection couldn't be made !!!")      

if __name__ == "__main__":
    main()

