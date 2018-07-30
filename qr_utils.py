import qrcode
import os
from PIL import Image


def make_qr(text):
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )

    qr.add_data(text)
    qr.make(fit=True)
    img = qr.make_image(fill_color='#00a680', back_color='white')
    
    return img


def make_qr_save(text, filepath):
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    img = make_qr(text)
    img.save(filepath)


def add_logo(qr, logo):
    icon = Image.open(logo)
    qr_w, qr_h = qr.size
 
    factor = 5
    size_w = int(qr_w / factor)
    size_h = int(qr_h / factor)
 
    icon_w, icon_h = icon.size
    if icon_w > size_w:
        icon_w = size_w
    if icon_h > size_h:
        icon_h = size_h
    icon = icon.resize((icon_w, icon_h), Image.ANTIALIAS)
 
    w = int((qr_w - icon_w) / 2)
    h = int((qr_h - icon_h) / 2)
    icon = icon.convert("RGBA")
    qr.paste(icon, (w, h), icon)
    
    return qr


def copy_qr(img_filepath, qr):
    background = Image.open(img_filepath)
    
    img_filename = os.path.basename(img_filepath)
    if img_filename == 'TA_Business-Card_1.png':
        qr = qr.resize((250, 250))
        background.paste(qr, (380, 275))
    elif img_filename == 'TA_Business-Card_2.png':
        qr = qr.resize((250, 250))
        background.paste(qr, (750, 40))
    elif img_filename == 'TA_Sticker.png':
        qr = qr.resize((250, 250))
        background.paste(qr, (350, 35))

    return background


def copy_qr_with_logo(img_filepath, text, filepath):
    qr = make_qr(text)
    output = copy_qr(img_filepath, qr)
    output.save(filepath)

# if __name__=='__main__':
#     path = 'logo_qrcode.png'
#     url = 'https://www.tripadvisor.com/Restaurant_Review-g32655-d348825-Reviews-Brent_s_Delicatessen_Restaurant-Los_Angeles_California.html'
#     img_filepath = 'TA_Sticker.png'
#     copy_qr_with_logo(img_filepath, url, path)

