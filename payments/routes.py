from payments import app
from flask import render_template, request
from payments.forms import PaymentsForm
from payments.piastrix_lib import PiastrixClient

secret_key = 'SecretKey01'
shop_id = '5'
payway = 'advcash_rub'  # only for invoice


@app.route('/', methods=['GET', 'POST'])
def payments():
    # TODO: to make description field in forms to return not a one word!!!
    # TODO: to un-hardcode shop_order_id
    # TODO: to fix functions' difference between type of data in requests and annotated type invoice()
    form = PaymentsForm()
    if request.method == 'POST':
        payment_api_class = PiastrixClient(shop_id, secret_key)

        if request.form.get("currency") == "978":  # currency - EUR
            amount = request.form.get("amount")
            currency = request.form.get("currency")
            shop_order_id = '102'
            extra_fields = {'description': request.form.get("description")}
            response = payment_api_class.pay(amount, currency, shop_order_id, extra_fields)
            print(response)
            # TODO: it is possible to add errors when displayiing resource
            return render_template('template_for_pay.html', form=form)

        elif request.form.get("currency") == "840":  # currency - USD
            shop_amount = request.form.get("amount")
            payer_currency = request.form.get("currency")
            shop_currency = request.form.get("currency")
            shop_order_id = '103'
            extra_fields = {'description': request.form.get("description")}
            response = payment_api_class.bill(payer_currency, shop_amount, shop_currency, shop_order_id, extra_fields)
            print(response)
            return response

        elif request.form.get("currency") == "643":  # currency - RUS
            amount = request.form.get("amount")
            currency = request.form.get("currency")
            shop_order_id = '101'
            extra_fields = {'description': request.form.get("description")}
            response = payment_api_class.invoice(amount, currency, shop_order_id, payway, extra_fields)
            print(response)
            return render_template('template_redirect_invoice.html', form=form)

    return render_template('payments.html', form=form)






