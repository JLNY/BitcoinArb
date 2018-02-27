
# A very simple Flask Hello World app for you to get started with...
import gdax
import gzip
import ast
from time import gmtime, strftime
from websocket import create_connection

from flask import Flask

app = Flask(__name__)

#GDAX price
def get_price_from_gdax(gdax_token):
    gdax_client = gdax.PublicClient()
    gdax_detail = gdax_client.get_product_ticker(product_id=gdax_token)
    return float(gdax_detail['price'])

#HUOBI
def get_price_from_huobi(huobi_token):
    ws = create_connection("wss://api.huobi.pro/ws")
    tradedetailstr = """{"req":"market."""+huobi_token+""".detail", "id": "id12"}"""
    ws.send(tradedetailstr)
    tradedetailcompressData=ws.recv()
    tradedetail=gzip.decompress(tradedetailcompressData).decode('utf-8')
    if tradedetail[:7] == '{"ping"':
        ts=tradedetail[8:21]
        pong='{"pong":'+ts+'}'
        ws.send(pong)
        ws.send(tradedetailstr)
    else:
        trade_detail = ast.literal_eval(tradedetail)
        return float(trade_detail['data']['close'])

def get_arbitrage_for_currecies(gdax_token, huobi_token):
    gdax_price = get_price_from_gdax(gdax_token)
    huobi_price = get_price_from_huobi(huobi_token)
    arbitrage_profit = (max(gdax_price, huobi_price) - min(gdax_price, huobi_price))/min(gdax_price, huobi_price)
    return arbitrage_profit



@app.route('/')
def hello_world():

    arb_btcusd = get_arbitrage_for_currecies('BTC-USD', 'btcusdt')
    arb_ethbtc = get_arbitrage_for_currecies('ETH-BTC', 'ethbtc')
    arb_ltcbtc = get_arbitrage_for_currecies('LTC-BTC', 'ltcbtc')
    # print(strftime("%Y-%m-%d %H:%M:%S", gmtime()) + ' BTC-USD : ' + str(arb_btcusd))
    # print(strftime("%Y-%m-%d %H:%M:%S", gmtime()) + ' ETH-BTC : ' + str(arb_ethbtc))
    # print(strftime("%Y-%m-%d %H:%M:%S", gmtime()) + ' LTC-BTC : ' + str(arb_ltcbtc))

    return str(arb_btcusd)