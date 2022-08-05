from cloudquant.interfaces import Strategy, Event
import ktgfunc

# Alerts generated using CloudQuant gui. Here are some of the ones I use

class Gr8Scripta95b1232657c4dc19a983dce8ff2c83b(Strategy):
    __script_name__ = '11___Alert_Dummy'

    def on_start(self, md, order, service, account):
        service.clear_event_triggers()
        service.add_event_trigger([md.symbol], [Event.TRADE])
        pass

    def on_trade(self, event, md, order, service, account):
        if ( True ):
            # 2% 12 MONTH LOW
            _alertList = [('Price', md.L1.last), ('Message', 'Stock has reached 2% of 12 Month Low')]
            service.alert( md.symbol, 'cf5a34c1-b6e5-4017-a316-cc652da9460f', _alertList )
            # NEW 12 MONTH LOW
            _alertList = [('Price', md.L1.last), ('Message', 'New 12 Month Low, Shorted Stock at __')]
            service.alert( md.symbol, '2785af4f-d521-4d26-b826-50c19f40e6cc', _alertList )
            # 2% 12 MONTH LOW
            _alertList = [('Price', md.L1.last), ('Message', 'Stock has reached 2% of 12 Month Low')]
            service.alert( md.symbol, 'cf5a34c1-b6e5-4017-a316-cc652da9460f', _alertList )
            # 2% 12 MONTH HIGH
            _alertList = [('Price', md.L1.last), ('Message', 'Stock has reached 2% of 12 Month High')]
            service.alert( md.symbol, '1fadb38a-4a12-4891-adee-d35fcca5e2be', _alertList )
            # NEW 12 MONTH HIGH
            _alertList = [('Price', md.L1.last), ('Message', 'New 12 Month High, Bought Stock')]
            service.alert( md.symbol, '44a652e4-c113-4512-8ce9-76e3cff8af6e', _alertList )
        else:
            # GAP DISTANCE
            _alertList = [('Price', md.L1.last), ('Message', 'Stock is trading $__ from gap up/down')]
            service.alert( md.symbol, 'be8e0dff-776c-4d26-8fb6-0a7f57a4cd93', _alertList )
            # GAP FILL
            _alertList = [('Price', md.L1.last), ('Message', 'Stock has filled _% of gap up/down')]
            service.alert( md.symbol, '32d92c42-96ea-43d1-b0fe-03ba948d761e', _alertList )
            # GAP FILLED
            _alertList = [('Price', md.L1.last), ('Message', 'Stocks Gap Filled')]
            service.alert( md.symbol, '0bb1857f-c00d-48bd-b1d9-6c22c07e8c17', _alertList )
            # HIGH VOL
            _alertList = [('Price', md.L1.last), ('Message', 'Stock is trading x% of its opening vol')]
            service.alert( md.symbol, 'b7069e93-0dc3-40e2-8224-c6d395088d39', _alertList )
            # IMBAL NOTION
            _alertList = [('Notional Value', 0.0)]
            service.alert( md.symbol, '396f9822-0544-4a31-82cf-b7d679b26542', _alertList )
            # INSIDE DAY
            _alertList = [('Price', md.L1.last), ('Message', 'Stock had an inside day yday')]
            service.alert( md.symbol, 'b64fc11b-a850-45dd-aea1-21ca84babe65', _alertList )

