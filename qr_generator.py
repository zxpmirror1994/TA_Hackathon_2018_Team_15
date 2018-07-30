import os
import psycopg2
import qr_utils


BASE_URL_DETAIL = 'https://www.tripadvisor.com/a-b-d{}-c'
BASE_URL_REVIEW = 'https://www.tripadvisor.com/UserReviewEdit-a-d{}-b-c'

IMPORTANT_COLS = [
    (8, 'country_primaryname'),
    (18, 'geo_name'),
    (0, 'location_id'),
    (17, 'geo_id'),
    (12, 'city_id'),
    (6, 'country_id'),
    (4, 'cont_id'),
    (32, 'is_accommodation'),
    (33, 'is_bnb'),
    (34, 'is_hotel'),
    (35, 'is_vr'),
    (36, 'is_resort'),
    (37, 'is_restaurant'),
    (38, 'is_attraction')
]

IMPORTANT_COL_HEADERS = {
    'country_primaryname': str,
    'geo_name': str,
    'location_id': int,
    'geo_id': int,
    'city_id': int,
    'country_id': int,
    'cont_id': int,
    'is_accommodation': int,
    'is_bnb': int,
    'is_hotel': int ,
    'is_vr': int,
    'is_resort': int,
    'is_restaurant': int,
    'is_attraction': int
}


colIdxToHeader = {
    0: 'location_id',
    1: 'property_name',
    2: 'place_type',
    3: 'inactive',
    4: 'cont_id',
    5: 'cont_primaryname',
    6: 'country_id',
    7: 'location_country_alltime_review_rank',
    8: 'country_primaryname',
    9: 'region_id',
    10: 'location_region_alltime_review_rank',
    11: 'region_primaryname',
    12: 'city_id',
    13: 'location_city_alltime_review_rank',
    14: 'city_primaryname',
    15: 'lattitude',
    16: 'longitude',
    17: 'geo_id',
    18: 'geo_name',
    19: 'geo_latitude',
    20: 'geo_longitude',
    21: 'karma',
    22: 'star_rating',
    23: 'accommodation_num_rooms',
    24: 'avg_price_w_fees',
    25: 'weekend_avg_price_w_fees',
    26: 'weekeday_avg_price_w_fees',
    27: 'distance_location_to_geo_center_km',
    28: 'hotel_type',
    29: 'hotel_category',
    30: 'attr_type',
    31: 'attr_category',
    32: 'is_accommodation',
    33: 'is_bnb',
    34: 'is_hotel',
    35: 'is_vr',
    36: 'is_resort',
    37: 'is_restaurant',
    38: 'is_attraction',
    39: 'bubble_score',
    40: 'current_popularity_score',
    41: 'last_popularity_score',
    42: 'alltime_review_count',
    43: 'alltime_5_review_count',
    44: 'alltime_4_review_count',
    45: 'lookback_review_count',
    46: 'lookback_5_review_count',
    47: 'lookback_4_review_count',
    48: 'city_cnt_accommodation',
    49: 'city_cnt_hotel',
    50: 'city_cnt_restaurant',
    51: 'city_cnt_attraction',
    52: 'city_cnt_resort',
    53: 'city_cnt_vr',
    54: 'city_alltime_review_count',
    55: 'region_cnt_accommodation',
    56: 'region_cnt_hotel',
    57: 'region_cnt_restaurant',
    58: 'region_cnt_attraction',
    59: 'region_cnt_resort',
    60: 'region_cnt_vr',
    61: 'region_alltime_review_count',
    62: 'country_cnt_accommodation',
    63: 'country_cnt_hotel',
    64: 'country_cnt_restaurant',
    65: 'country_cnt_attraction',
    66: 'country_cnt_resort',
    67: 'country_cnt_vr',
    68: 'country_alltime_review_count',
    69: 'geo_cnt_accommodation',
    70: 'geo_cnt_hotel',
    71: 'geo_cnt_restaurant',
    72: 'geo_cnt_attraction',
    73: 'geo_cnt_resort',
    74: 'geo_cnt_vr',
    75: 'geo_alltime_review_count',
    76: 'geo_total_room_count',
    77: 'geo_avg_price_w_fees',
    78: 'geo_weekend_avg_price_w_fees',
    79: 'geo_weekeday_avg_price_w_fees',
    80: 'geo_furthest_hotel_km',
    81: 'geo_furthest_poi_km',
    82: 'accomodation_geo_price_rank',
    83: 'accomodation_geo_num_rooms_rank',
    84: 'accomodation_geo_total_value_rank',
    85: 'accomodation_pop_rank',
    86: 'accomodation_country_price_rank',
    87: 'accomodation_country_num_rooms_rank',
    88: 'accomodation_country_total_value_rank',
    89: 'brand_name',
    90: 'parent_brand_name',
    91: 't4b_package_id',
    92: 't4b_package_description',
    93: 't4b_package_tier'
}


class Rio:
    def __init__(self):
        pass

    def query(self, query, params=()):
        # Relies on .pgpass for authentication
        conn = psycopg2.connect(dbname='rio', host='rio-proxy.tripadvisor.com', port='5439', user='skhetan', password='K@m@1y@H')
        cur = conn.cursor()
        cur.execute(query, params)
        return cur

    def query_simple(self, query):
        cur = self.query(query)
        if cur:
            result = cur.fetchall()
            if result:
                return result
        return None


def _add_restriction(query_middle, statement):
    if len(statement) == 0 or not any(statement.values()):
        return

    if len(query_middle) == 0:
        query_middle.append('WHERE')
    else:
        query_middle.append('AND')

    to_append = []
    for key, val in statement.items():
        if val:
            if isinstance(val, str):
                text = "{}='{}'".format(key, val)
            else:
                text = '{}={}'.format(key, val)

            if len(to_append) == 0:
                to_append.append('({}'.format(text))
            else:
                to_append.append('OR {}'.format(text))

    if len(to_append) > 0:
        to_append[-1] = to_append[-1] + ')'
    query_middle += to_append


def _create_query(
    location_id,
    geo_name,
    country_primaryname,
    geo_id,
    city_id,
    country_id,
    cont_id,
    is_accomodation,
    is_bnb,
    is_hotel,
    is_vr,
    is_resort,
    is_restaurant,
    is_attraction,
    limit
    ):
    restrictions = [
        { 'location_id': location_id },
        { 'geo_name': geo_name },
        { 'country_primaryname': country_primaryname },
        { 'geo_id': geo_id },
        { 'city_id': city_id },
        { 'country_id': country_id },
        { 'cont_id': cont_id },
        {
            'is_accommodation': is_accomodation,
            'is_bnb': is_bnb,
            'is_hotel': is_hotel,
            'is_vr': is_vr,
            'is_resort': is_resort,
            'is_restaurant': is_restaurant,
            'is_attraction': is_attraction
        }
        ]

    start = ['SELECT * FROM revops.location_tree']
    middle = []
    end = ['LIMIT {};'.format(limit)]

    for statement in restrictions:
        if statement:
            _add_restriction(middle, statement)

    return ' '.join(start + middle + end)


'''
URL?country_primaryname=...&geo_name=...&...
'''

def create_files(
    location_id=None,
    geo_name=None,
    country_primaryname=None,
    geo_id=None,
    city_id=None,
    country_id=None,
    cont_id=None,
    is_accomodation=1,
    is_bnb=1,
    is_hotel=1,
    is_vr=1,
    is_resort=1,
    is_restaurant=1,
    is_attraction=1,
    limit=100,
    img_dir='./resources',
    asset_filepath='',
    details_or_reviews='details'
    ):

    query = _create_query(
        location_id=location_id,
        geo_name=geo_name,
        country_primaryname=country_primaryname,
        geo_id=geo_id,
        city_id=city_id,
        country_id=country_id,
        cont_id=cont_id,
        is_accomodation=is_accomodation,
        is_bnb=is_bnb,
        is_hotel=is_hotel,
        is_vr=is_vr,
        is_resort=is_resort,
        is_restaurant=is_restaurant,
        is_attraction=is_attraction,
        limit=limit
        )

    results = Rio().query_simple(query)
    
    generated = []

    if results:
        for result in results:
            info = {}
            for i, name in IMPORTANT_COLS:
                info[name] = result[i]

            if details_or_reviews == 'details':
                url = BASE_URL_DETAIL.format(info['location_id'])
            elif details_or_reviews == 'reviews':
                url = BASE_URL_REVIEW.format(info['location_id'])

            '''
            subdirname = '{}-{}'.format(
                info['country_primaryname'], 
                info['geo_name']
                )
            dirpath = os.path.join(img_dir, asset_dir, subdirname).replace(' ', '_')
            '''
            asset_dir = 'QR_code'
            if len(asset_filepath) > 0:
                asset_dir = os.path.basename(asset_filepath).replace('.png', '')
            
            dirpath = os.path.join(img_dir, asset_dir).replace(' ', '_')
            if not os.path.isdir(dirpath):
                os.makedirs(dirpath)

            filename = '{}.png'.format(
                info['location_id'])
            filepath = os.path.join(dirpath, filename).replace(' ', '_')

            ret_info = {}
            ret_info['property_name'] = result[1]
            ret_info['url'] = url
            ret_info['filepath'] = filepath
            generated.append(ret_info)

            if asset_filepath:
                qr_utils.copy_qr_with_logo(asset_filepath, url, filepath)
            else:
                qr_utils.make_qr_save(url, filepath)

    return generated


if __name__ == '__main__':
    create_files(
        geo_name='Boston',
        )





