import razorpay
from django.conf import settings


def is_configured():
    return bool(settings.RAZORPAY_KEY_ID and settings.RAZORPAY_KEY_SECRET)


def get_client():
    if not is_configured():
        raise RuntimeError("Razorpay keys are not set — add RAZORPAY_KEY_ID / RAZORPAY_KEY_SECRET to .env")
    return razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))


def create_razorpay_order(amount_rupees, receipt):
    """
    Creates an order on Razorpay's side for the given amount (in rupees).
    Razorpay works in paise, so we multiply by 100. Returns the order dict,
    which includes an 'id' you pass to the frontend Checkout widget.
    """
    client = get_client()
    amount_paise = int(round(float(amount_rupees) * 100))
    return client.order.create({
        'amount': amount_paise,
        'currency': 'INR',
        'receipt': receipt,
        'payment_capture': 1,  # auto-capture instead of authorize-only
    })


def verify_payment_signature(razorpay_order_id, razorpay_payment_id, razorpay_signature):
    """
    Returns True if the signature Razorpay's Checkout widget handed back to
    the browser is genuinely from Razorpay (not forged/tampered by the
    client). Always call this before trusting a "payment succeeded" message
    from the frontend — never mark an order paid on the JS callback alone.
    """
    client = get_client()
    try:
        client.utility.verify_payment_signature({
            'razorpay_order_id': razorpay_order_id,
            'razorpay_payment_id': razorpay_payment_id,
            'razorpay_signature': razorpay_signature,
        })
        return True
    except razorpay.errors.SignatureVerificationError:
        return False
