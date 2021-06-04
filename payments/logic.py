from hashlib import sha256
from urllib.parse import urljoin
import requests
import logging

# creating and setting up a logger
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

formatter = logging.Formatter('%(asctime)s:%(name)s:%(message)s')

file_handler = logging.FileHandler('routes.log')
file_handler.setFormatter(formatter)

logger.addHandler(file_handler)


class Payments:

    """Creating a class which handles logic for three payment scenarios: PAY, Bill and Invoice"""

    def __init__(self, shop_id, secret_key, timeout=10, url='https://core.piastrix.com/'):
        self.shop_id = shop_id
        self.secret_key = secret_key
        self.timeout = timeout
        self.piastrix_url = url

    def _sign(self, data, required_fields):

        """Creating a hash sha256 for 'required_fields' """

        sorted_data = [data[key] for key in sorted(required_fields)]
        signed_data = ':'.join(sorted_data) + self.secret_key
        data['sign'] = sha256(signed_data.encode('utf-8')).hexdigest()

    def _post(self, endpoint, req_dict):

        """sending data to the server"""

        response = requests.post(urljoin(self.piastrix_url, endpoint), json=req_dict, timeout=self.timeout)
        logger.debug(req_dict)  # logging a data which is being sent to server
        response.raise_for_status()
        result = response.json()
        if result['result'] is True:
            return result.get('data')

    def pay(self, amount: float, currency: int, shop_order_id: str,
            extra_fields: dict or None = None) -> tuple:

        """ logic for Invoice payment scenario """

        required_fields = ['amount', 'currency', 'shop_id', 'shop_order_id']
        form_data = {
            "amount": amount,
            "shop_id": self.shop_id,
            "currency": currency,
            "shop_order_id": shop_order_id
        }
        if extra_fields is not None:
            form_data.update(extra_fields)
        self._sign(form_data, required_fields)
        logger.debug(form_data)  # logging
        url = f"https://pay.piastrix.com/en/pay"
        return form_data, url

    def invoice(self, amount: float, currency: int, shop_order_id: str,
                payway: str, extra_fields: dict or None = None) -> dict:

        """ logic for Invoice payment scenario """

        required_fields = ['amount', 'currency', 'shop_id', 'payway', 'shop_order_id']
        req_dict = {
            "amount": amount,
            "currency": currency,
            "shop_id": self.shop_id,
            "payway": payway,
            "shop_order_id": shop_order_id
        }
        if extra_fields is not None:
            req_dict.update(extra_fields)
        self._sign(req_dict, required_fields)
        return self._post('invoice/create', req_dict)

    def bill(self, payer_currency: int, shop_amount: float, shop_currency: int,
             shop_order_id: str, extra_fields: dict or None = None) -> dict:

        """ logic for Bill payment scenario """

        required_fields = ['payer_currency', 'shop_amount', 'shop_currency', 'shop_id', 'shop_order_id']
        req_dict = {
            "payer_currency": payer_currency,
            "shop_amount": shop_amount,
            "shop_currency": shop_currency,
            "shop_id": self.shop_id,
            "shop_order_id": shop_order_id
        }
        if extra_fields is not None:
            req_dict.update(extra_fields)
        self._sign(req_dict, required_fields)
        return self._post('bill/create', req_dict)
