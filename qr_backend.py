from flask import Flask, send_file, request, render_template
import qr_generator as qrgen
import os

app = Flask(__name__)

IMG_DIR = './resources'
STYLE_DIR = './style'

ASSET_NAME_CHOICES = {
    'QR Code Image' : '',
    'Stickers': './assets/TA_Sticker.png', 
    'Business Cards Type 1': './assets/TA_Business-Card_1.png', 
    'Business Cards Type 2': './assets/TA_Business-Card_2.png'
}

DETAILS_OR_REVIEWS_CHOICES = {
    'Detail Page': 'details',
    'Write a Review Page': 'reviews'
}

PROPERTY_CHOICES = {
    'Rod Thai Cuisine': 321615, 
    "Al's State Street Cafe": 321663,
    'Hungry Travelers': 321669, 
    'Pho Pasteur': 321744, 
    'Philadelphia Steak & Hoagie': 321787
}


@app.route("/user")
def user():
    return render_template('user_template.html')


@app.route("/user/onsubmit")
def user_onsubmit():
    if 'property_choice' not in request.args:
        return 'You must enter a property choice'
    if 'details_or_reviews' not in request.args:
        return 'You must choose either details or reviews'
    if 'asset_name' not in request.args:
        return 'You must select a TripAdvisor marketing asset'

    details_or_reviews = request.args.get('details_or_reviews')
    if details_or_reviews not in DETAILS_OR_REVIEWS_CHOICES:
        return 'Invalid details or reviews selection'
    asset_name = request.args.get('asset_name')
    if asset_name not in ASSET_NAME_CHOICES:
        print(ASSET_NAME_CHOICES)
        return 'Invalid marketing asset name selection'
    property_choice = request.args.get('property_choice')
    if property_choice not in PROPERTY_CHOICES:
        return 'Invalid property choice'
    
    detrev_val = DETAILS_OR_REVIEWS_CHOICES[details_or_reviews]
    asset_path = ASSET_NAME_CHOICES[asset_name]
    location_id = PROPERTY_CHOICES[property_choice]

    outpath = os.path.join(IMG_DIR, os.path.basename(asset_path).replace('.png', ''), str(location_id) + '.png')
    if asset_path and os.path.isfile(outpath):
        return render_template('user_template_onsubmit.html', qr_path=os.path.join('..', outpath))

    generated = qrgen.create_files(
        location_id = location_id,
        img_dir = IMG_DIR,
        asset_filepath = asset_path,
        details_or_reviews=detrev_val
    )
    if len(generated) == 0:
        return 'No generated file, location ID likely does not exist.'
    else:
        return render_template('user_template_onsubmit.html', qr_path=os.path.join('..', generated[0]['filepath']))
    return 'Location ID is missing or malformed.'


@app.route("/resources/<asset_name>/<file_path>")
def get_img(asset_name, file_path):
    fullpath = os.path.join(IMG_DIR, asset_name, file_path)
    if os.path.isfile(fullpath):
        return send_file(fullpath)
    return 'File not found on server'


@app.route("/style/<filename>")
def get_style(filename):
    print(filename)
    fullpath = os.path.join(STYLE_DIR, filename)
    if os.path.isfile(fullpath):
        return send_file(fullpath)
    return 'File not found on server'


@app.route("/biz")
def business():
    return render_template('biz_template.html')


@app.route("/biz/onsubmit")
def business_onsubmit():
    if 'details_or_reviews' not in request.args:
        return 'You must choose either details or reviews'
    if 'asset_name' not in request.args:
        return 'You must select a TripAdvisor marketing asset'

    details_or_reviews = request.args.get('details_or_reviews')
    if details_or_reviews not in DETAILS_OR_REVIEWS_CHOICES:
        return 'Invalid details or reviews selection'
    asset_name = request.args.get('asset_name')
    if asset_name not in ASSET_NAME_CHOICES:
        return 'Invalid marketing asset name selection'

    detrev_val = DETAILS_OR_REVIEWS_CHOICES[details_or_reviews]
    asset_path = ASSET_NAME_CHOICES[asset_name]

    if 'location_id' in request.args and request.args['location_id'].isdigit():
        location_id = request.args.get('location_id')
        outpath = os.path.join(IMG_DIR, os.path.basename(asset_path).replace('.png', ''), str(location_id) + '.png')
        if asset_path and os.path.isfile(outpath):
            return render_template('biz_template_onsubmit_single.html', qr_path=os.path.join('..', outpath))

        generated = qrgen.create_files(
            location_id = request.args['location_id'],
            img_dir = IMG_DIR,
            asset_filepath = asset_path,
            details_or_reviews=detrev_val
        )
        if len(generated) == 0:
            return 'No generated file, location ID likely does not exist.'
        else:
            return render_template('biz_template_onsubmit_single.html', qr_path=os.path.join('..', generated[0]['filepath']))

    else:
        db_params = []
        for param in qrgen.IMPORTANT_COL_HEADERS:
            if param in request.args:
                if qrgen.IMPORTANT_COL_HEADERS[param] == int and param.isdigit():
                    db_params.append(param)
                elif qrgen.IMPORTANT_COL_HEADERS[param] == str and len(param) > 0:
                    db_params.append(param)

        qr_args = {}
        for param in db_params:
            qr_args[param] = request.args[param]

        for param in ['is_accomodation', 'is_bnb', 'is_hotel', 'is_vr', 'is_resort', 'is_restaurant', 'is_attraction']:
            qr_args[param] = int(param in request.args)

        qr_args['img_dir'] = IMG_DIR
        qr_args['asset_filepath'] = asset_path
        qr_args['details_or_reviews'] = detrev_val

        generated = qrgen.create_files(**qr_args)

        return render_template('biz_template_onsubmit.html', generated=generated)


    '''
    create_files_args = zip((param, request.args[param]) for param in db_params)
    qrgen.create_files(**create_files_args)
    '''



    '''
    qrgen.create_files(
        location_id=105250
        )
    '''
    # return send_file('./United States-Boston/105250.png')

