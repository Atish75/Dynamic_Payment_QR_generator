import qrcode
import base64
from io import BytesIO
from urllib.parse import urlencode, quote

from django.contrib import messages
from django.shortcuts import render, redirect
from .models import UPISettings


def generate_qr(request):
    config = UPISettings.get()
    if not config:
        return redirect("upi_settings")

    qr_image = customer_name = amount = note = None
    # Aapka real banking name jo customer ko scan karte waqt dikhega
    store_banking_name = getattr(config, "banking_name", "") or "Store Payment"

    if request.method == "POST":
        customer_name = request.POST.get("name", "").strip()
        amount = request.POST.get("amount", "").strip()
        note = request.POST.get("note", "").strip()

        # Customer ka naam aur note ko Transaction Note (tn) mein combine karein
        if customer_name and note:
            txn_note = f"{customer_name} ({note})"
        elif customer_name:
            txn_note = f"Customer: {customer_name}"
        else:
            txn_note = note

        params = {
            "pa": config.upi_id,
            "pn": store_banking_name,  # Scan karne par aapka banking name dikhega
            "cu": "INR",
        }
        if amount:
            params["am"] = amount
        if txn_note:
            params["tn"] = txn_note

        upi_uri = "upi://pay?" + urlencode(params, quote_via=quote)

        qr = qrcode.make(upi_uri)
        buffer = BytesIO()
        qr.save(buffer, format="PNG")
        qr_image = base64.b64encode(buffer.getvalue()).decode()

    return render(request, "qrcode.html", {
        "qr_image": qr_image,
        "upi_id": config.upi_id,
        "banking_name": store_banking_name,
        "name": customer_name,
        "amount": amount,
        "note": note,
    })

def upi_settings(request):
    config = UPISettings.get()

    if request.method == "POST":
        new_upi = request.POST.get("new_upi_id", "").strip()
        password = request.POST.get("password", "")

        if not new_upi or "@" not in new_upi:
            messages.error(request, "Valid UPI ID daalo (example: name@bank)")
        elif config is None:
            # first-time setup
            if len(password) < 6:
                messages.error(request, "Password kam se kam 6 characters ka rakho")
            else:
                config = UPISettings(upi_id=new_upi)
                config.set_password(password)
                config.save()
                messages.success(request, "UPI ID aur password set ho gaya")
                return redirect("generate_qr")
        else:
            # change: purana password zaroori
            if not config.verify_password(password):
                messages.error(request, "Galat password")
            else:
                config.upi_id = new_upi
                config.save()
                messages.success(request, "UPI ID update ho gayi")
                return redirect("generate_qr")

    return render(request, "upi_settings.html", {
        "config": config,
        "first_time": config is None,
    })