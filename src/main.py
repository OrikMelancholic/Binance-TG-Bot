from binance_connector import BinanceConnector
from binance import Client
import matplotlib.pyplot as plt


if __name__ == '__main__':
    bc = BinanceConnector()

    data = bc.get_data("BNBBTC", Client.KLINE_INTERVAL_15MINUTE, "15 Nov, 2021")

    print(data)

    data_prepaired = data['median'].to_numpy()
    lenght = list(range(0, len(data['median'])))
    plt.subplot(1, 1, 1)
    plt.plot(lenght, data_prepaired)
    plt.savefig('test_fig.png')
    plt.show()


