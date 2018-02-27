import gdax
import gzip
import ast
import csv
from time import gmtime, strftime, localtime
import time
from websocket import create_connection
from urllib import request
import krakenex
from pykrakenapi import KrakenAPI
import psycopg2


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

#Kraken
def get_price_from_kraken(kraken_token):
    krakenApi = KrakenAPI(krakenex.API());
    krakenprice = krakenApi.get_ticker_information(kraken_token).loc[kraken_token]['a'][0]
    return float(krakenprice)

#saveDataToDB
def save_data_to_DB(command):
    conn = psycopg2.connect("dbname='BitCoinArb' user=postgres password=postgres")
    # command = """
    #     CREATE TABLE Price (
    #         time TIMESTAMP ,
    #         token VARCHAR(50),
    #         profit FLOAT
    #     )
    #     """
    cur = conn.cursor()
    cur.execute(command)
    cur.close()
    conn.commit()

def save_price_to_DB(timestamp, token, profit):
    sqlbase = """
        INSERT INTO price(datetime, token, profit)
        VALUES (CURRENT_TIMESTAMP , '%s', %f);
    """
    sql = sqlbase % (token, profit)
    save_data_to_DB(sql)

def get_arbitrage_for_currecies(gdax_token, huobi_token, kraken_token = 'XXBTZUSD'):
    gdax_price = get_price_from_gdax(gdax_token)
    huobi_price = get_price_from_huobi(huobi_token)
    kraken_price = get_price_from_kraken(kraken_token)
    arbitrage_profit = (max(gdax_price, huobi_price, kraken_price) - min(gdax_price, huobi_price, kraken_price))/min(gdax_price, huobi_price, kraken_price)
    return arbitrage_profit

if __name__ == '__main__':
    while(1):
        arb_btcusd = get_arbitrage_for_currecies('BTC-USD', 'btcusdt', 'XXBTZUSD')
        save_price_to_DB(time.time(), 'BTC-USD', arb_btcusd)
        arb_ethbtc = get_arbitrage_for_currecies('ETH-BTC', 'ethbtc', 'XETHXXBT')
        save_price_to_DB(time.time(), 'ETH-BTC', arb_ethbtc)
        arb_ltcbtc = get_arbitrage_for_currecies('LTC-BTC', 'ltcbtc', 'XLTCXXBT')
        save_price_to_DB(time.time(), 'LTC-BTC', arb_ltcbtc)
    # with open('E://BitCoin//arbitrage.csv', 'w', newline='') as csvfile:
    #     csvwriter = csv.writer(csvfile, delimiter=' ')
    #     while(1):
    #         arb_btcusd = get_arbitrage_for_currecies('BTC-USD', 'btcusdt', 'XXBTZUSD')
    #         arb_ethbtc = get_arbitrage_for_currecies('ETH-BTC', 'ethbtc', 'XETHXXBT')
    #         arb_ltcbtc = get_arbitrage_for_currecies('LTC-BTC', 'ltcbtc', 'XLTCXXBT')
    #         csvwriter.writerow(strftime("%Y-%m-%d %H:%M:%S", gmtime()) + ', BTC-USD, ' + str(arb_btcusd))
    #         csvwriter.writerow(strftime("%Y-%m-%d %H:%M:%S", gmtime()) + ', ETH-BTC, ' + str(arb_ethbtc))
    #         csvwriter.writerow(strftime("%Y-%m-%d %H:%M:%S", gmtime()) + ', LTC-BTC, ' + str(arb_ltcbtc))
    #         print(strftime("%Y-%m-%d %H:%M:%S", gmtime()) + ', BTC-USD, ' + str(arb_btcusd))
    #         print(strftime("%Y-%m-%d %H:%M:%S", gmtime()) + ', ETH-BTC, ' + str(arb_ethbtc))
    #         print(strftime("%Y-%m-%d %H:%M:%S", gmtime()) + ', LTC-BTC, ' + str(arb_ltcbtc))




# public_client = gdax.PublicClient()
#
# btcusd = public_client.get_product_ticker(product_id='BTC-USD')
# btceth = public_client.get_product_ticker(product_id='ETH-BTC')
# print('BTC-USD : ' + btcusd['price'])
# print('ETH-BTC : ' + btceth['price'])
#
# #HUOBI price
# ws = create_connection("wss://api.huobi.pro/ws")
# tradedetailstr = """{"req":"market.btcusdt.detail", "id": "id12"}"""
# ws.send(tradedetailstr)
# #while(1):
# tradedetailcompressData=ws.recv()
# tradedetail=gzip.decompress(tradedetailcompressData).decode('utf-8')
# if tradedetail[:7] == '{"ping"':
#     ts=tradedetail[8:21]
#     pong='{"pong":'+ts+'}'
#     ws.send(pong)
#     ws.send(tradedetailstr)
# else:
#     trade_detail = ast.literal_eval(tradedetail)
#     print('BTC-USD : ' + str(trade_detail['data']['close']))
#

# ws = create_connection("wss://api.huobi.pro/ws")
# huobi_ethbtc_detail_req = """{"req":"market.ethbtc.detail", "id": "id12"}"""
# ws.send(huobi_ethbtc_detail_req)
# #while(1):
# huobi_ethbtc_compress_data=ws.recv()
# huobi_ethbtc_data_str=gzip.decompress(huobi_ethbtc_compress_data).decode('utf-8')
# if huobi_ethbtc_data_str[:7] == '{"ping"':
#     ts=huobi_ethbtc_data_str[8:21]
#     pong='{"pong":'+ts+'}'
#     ws.send(pong)
#     ws.send(huobi_ethbtc_detail_req)
# else:
#     huobi_ethbtc_detail = ast.literal_eval(huobi_ethbtc_data_str)
#     print('ETH-BTC: ' + str(huobi_ethbtc_detail['data']['close']))