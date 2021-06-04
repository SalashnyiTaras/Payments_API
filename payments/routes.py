from flask import render_template, request, redirect, flash
from payments import app
from payments.forms import PaymentsForm
from payments.logic import Payments, logger

secret_key = 'SecretKey01'
shop_id = '5'
payway = 'advcash_rub'  # only for invoice


@app.route('/', methods=['GET', 'POST'])
def payments():

    """Function payments is a form which needs to be field in order to make a payment. There are needs to be filled
    following fields: amount, currency and description. Based on chosen currency one of three different scenarios will
    be applied: EUR - scenario 1, USD - scenario 1, RUB - scenario 3"""

    form = PaymentsForm()

    if request.method == 'POST':

        payment_api_class = Payments(shop_id, secret_key)

        if form.validate_on_submit():

            if request.form.get("currency") == "978":  # Scenario 1: when currency - EUR. Protocol - PAY
                amount = (request.form.get("amount"))
                currency = (request.form.get("currency"))
                currency_to_display_html = "EURO"
                shop_order_id = '102'
                extra_fields = {'description': request.form.get("description")}
                response = payment_api_class.pay(amount, currency, shop_order_id, extra_fields)
                print(request.form)
                return render_template('template_for_pay.html', shop_id=shop_id, shop_order_id=shop_order_id,
                                       sign=response[0]['sign'], form=form,
                                       currency_to_display_html=currency_to_display_html)

            elif request.form.get("currency") == "840":  # Scenario 2: when currency - USD. Protocol - Bill.
                shop_amount = request.form.get("amount")
                payer_currency = request.form.get("currency")
                shop_currency = request.form.get("currency")
                shop_order_id = '103'
                extra_fields = {'description': request.form.get("description")}
                payment_api_class.bill(payer_currency, shop_amount, shop_currency, shop_order_id, extra_fields)
                return redirect("https://wallet.piastrix.com/ru/bill/pay/ksUyhvPvvaagmixjw", code=302)

            elif request.form.get("currency") == "643":  # Scenario 3: when currency - RUB. Protocol - Invoice.
                amount = request.form.get("amount")
                currency = request.form.get("currency")
                currency_to_display_html = "RUB"
                shop_order_id = '101'
                extra_fields = {'description': request.form.get("description")}
                payment_api_class.invoice(amount, currency, shop_order_id, payway, extra_fields)
                return render_template('template_redirect_invoice.html', form=form,
                                       currency_to_display_html=currency_to_display_html)

        if form.errors != {}:  # checking if there is any validation error
            for err_msg in form.errors.values():
                logger.error(f"Error in submitting the form: {err_msg}")  # logging errors
                flash(f"Error when submitting the form: {err_msg}", category='danger')  # displaying errors in html

    return render_template('payments.html', form=form)
