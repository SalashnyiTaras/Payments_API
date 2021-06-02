from datetime import datetime
from hashlib import sha256
from urllib.parse import urljoin
import requests


class PiastrixClientException(Exception):
    def __init__(self, message, error_code):
        self.error_code = error_code
        super().__init__(message)


class PiastrixErrorCode:
    ExtraFieldsError = 1000
    IpError = 1001
    SignError = 1002
    ShopAmountError = 1003
    ShopCurrencyError = 1004
    StatusError = 1005
    LanguageError = 1006
    AmountTypeError = 1007


class PiastrixClient:
    def __init__(self, shop_id, secret_key, timeout=10, url='https://core.piastrix.com/'):
        self.shop_id = shop_id
        self.secret_key = secret_key
        self.timeout = timeout
        self.piastrix_url = url

    def _sign(self, data, required_fields):
        sorted_data = [data[key] for key in sorted(required_fields)]
        signed_data = ':'.join(sorted_data) + self.secret_key
        data['sign'] = sha256(signed_data.encode('utf-8')).hexdigest()

    def _post(self, endpoint, req_dict):
        response = requests.post(urljoin(self.piastrix_url, endpoint), json=req_dict, timeout=self.timeout)
        response.raise_for_status()
        result = response.json()
        if result['result'] is True:
            return result.get('data')
        raise PiastrixClientException(result['message'], result['error_code'])

    def _check_extra_fields_keys(self, extra_fields, req_dict):
        for key in extra_fields:
            if key in req_dict:
                raise PiastrixClientException("Wrong key in extra_fields. Don't use the same keys as req_dict",
                                              PiastrixErrorCode.ExtraFieldsError)

    def check_callback(self, request_data: dict, remote_ip_address: str,
                       shop_amount: float, shop_currency: int) -> None:
        """Check callback method  for invoice and bill
        https://piastrix.docs.apiary.io/#reference/bill,-invoice-callback

        Parameters:
                request_data: dict
                remote_ip_address: str
                shop_amount: float
                shop_currency: int

        Returns:
                None, (if something is wrong - raise PiastrixClientException)

        """
        allowed_ip_address = [
            '87.98.145.206',
            '51.68.53.104',
            '51.68.53.105',
            '51.68.53.106',
            '51.68.53.107',
            '91.121.216.63',
            '37.48.108.180',
            '37.48.108.181'
        ]
        sign = request_data.pop('sign')
        if remote_ip_address not in allowed_ip_address:
            raise PiastrixClientException('IP address is not in allowed IP addresses',
                                          PiastrixErrorCode.IpError)
        required_fields = [key for key in request_data.keys() if request_data[key] not in ['', None]]
        self._sign(request_data, required_fields)
        if sign != request_data['sign']:
            raise PiastrixClientException('Wrong sign', PiastrixErrorCode.SignError)
        if shop_amount != request_data['shop_amount']:
            raise PiastrixClientException('Wrong shop_amount',
                                          PiastrixErrorCode.ShopAmountError)
        if shop_currency != request_data['shop_currency']:
            raise PiastrixClientException('Wrong shop_currency',
                                          PiastrixErrorCode.ShopCurrencyError)
        if request_data['status'] != 'success':
            raise PiastrixClientException('Wrong status',
                                          PiastrixErrorCode.StatusError)

    def invoice(self, amount: float, currency: int, shop_order_id: str,
                payway: str, extra_fields: dict or None = None) -> dict:
        """Billing for other currencies - invoice method
        https://piastrix.docs.apiary.io/#reference/api-invoice/-invoice

        Parameters:
            amount: float
            currency: int
            shop_order_id: str
            payway: str
            extra_fields: dict or None (influencing keys: description, phone, failed_url,
                            success_url, callback_url)

        Returns:
            response: dict (with keys: data(customerNumber, orderNumber, paymentType, scid,
                    shopArticleId, shopFailURL, shopId, shopSuccessURL, sum), id, method, url)

        """
        required_fields = ['amount', 'currency', 'shop_id', 'payway', 'shop_order_id']
        req_dict = {
            "amount": amount,
            "currency": currency,
            "shop_id": self.shop_id,
            "payway": payway,
            "shop_order_id": shop_order_id
        }
        if extra_fields is not None:
            self._check_extra_fields_keys(extra_fields, req_dict)
            req_dict.update(extra_fields)
        self._sign(req_dict, required_fields)
        return self._post('invoice/create', req_dict)

    def pay(self, amount: float, currency: int, shop_order_id: str,
            extra_fields: dict or None = None) -> tuple:
        """Billing for payment with pay method
        https://piastrix.docs.apiary.io/#introduction/pay/pay

        Parameters:
            amount: float
            currency: int
            shop_order_id: str
            extra_fields: dict or None (influencing keys: description, payway, payer_account,
                    failed_url, success_url, callback_url)
            lang: str ('ru' or 'en', default='ru')

        Returns:
            response: tuple (dict (with keys: amount, shop_id, currency, shop_order_id,
                    description, sign) and url)

        """
        required_fields = ['amount', 'currency', 'shop_id', 'shop_order_id']
        form_data = {
            "amount": amount,
            "shop_id": self.shop_id,
            "currency": currency,
            "shop_order_id": shop_order_id
        }
        if extra_fields is not None:
            self._check_extra_fields_keys(extra_fields, form_data)
            form_data.update(extra_fields)
        self._sign(form_data, required_fields)
        url = f"https://pay.piastrix.com/en/pay"
        return form_data, url

    def bill(self, payer_currency: int, shop_amount: float, shop_currency: int,
             shop_order_id: str, extra_fields: dict or None = None) -> dict:
        """Billing for payment - bill method
        https://piastrix.docs.apiary.io/#reference/0/-piastix-bill/0
        Parameters:
            payer_currency: int
            shop_amount: float
            shop_currency: int
            shop_order_id: str
            extra_fields: dict or None (influencing keys: description, payer_account, failed_url,
                            success_url, callback_url)
        Returns:
            response: dict (with keys: created, id, lifetime, payer_account,
                    payer_currency, payer_price, shop_amount, shop_currency,
                    shop_id, shop_order_id, shop_refund, url)
        """
        required_fields = ['payer_currency', 'shop_amount', 'shop_currency', 'shop_id', 'shop_order_id']
        req_dict = {
            "payer_currency": payer_currency,
            "shop_amount": shop_amount,
            "shop_currency": shop_currency,
            "shop_id": self.shop_id,
            "shop_order_id": shop_order_id
        }
        if extra_fields is not None:
            self._check_extra_fields_keys(extra_fields, req_dict)
            req_dict.update(extra_fields)
        self._sign(req_dict, required_fields)
        return self._post('bill/create', req_dict)