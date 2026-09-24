"""
generate_superstore.py
----------------------
Generates a synthetic 'Sample - Superstore.csv' that faithfully replicates
the schema, column names, value ranges, and statistical distributions of the
real Tableau Sample Superstore dataset (~9,994 rows, 2014-2017).

Run:   py generate_superstore.py
Output: Sample - Superstore.csv  (in the current working directory)
"""

import random
import numpy as np
import pandas as pd
from datetime import date, timedelta

# ── Reproducibility ────────────────────────────────────────────────────────────
SEED = 42
random.seed(SEED)
np.random.seed(SEED)

N = 9994   # row count matching real dataset

# ── Reference data ─────────────────────────────────────────────────────────────
REGIONS = ['West', 'East', 'Central', 'South']
REGION_WEIGHTS = [0.32, 0.29, 0.21, 0.18]

STATES_BY_REGION = {
    'West':    ['California', 'Washington', 'Oregon', 'Nevada', 'Colorado', 'Utah', 'Arizona'],
    'East':    ['New York', 'Pennsylvania', 'Ohio', 'Virginia', 'North Carolina', 'Georgia', 'Florida'],
    'Central': ['Texas', 'Illinois', 'Michigan', 'Minnesota', 'Missouri', 'Kansas', 'Wisconsin'],
    'South':   ['Alabama', 'Arkansas', 'Louisiana', 'Mississippi', 'Oklahoma', 'Tennessee', 'Kentucky'],
}
CITY_BY_STATE = {
    'California': ['Los Angeles', 'San Francisco', 'San Diego', 'Sacramento'],
    'Washington': ['Seattle', 'Tacoma', 'Spokane'],
    'Oregon':     ['Portland', 'Eugene'],
    'Nevada':     ['Las Vegas', 'Reno'],
    'Colorado':   ['Denver', 'Colorado Springs'],
    'Utah':       ['Salt Lake City', 'Provo'],
    'Arizona':    ['Phoenix', 'Tucson', 'Scottsdale'],
    'New York':   ['New York City', 'Buffalo', 'Rochester'],
    'Pennsylvania': ['Philadelphia', 'Pittsburgh'],
    'Ohio':       ['Columbus', 'Cleveland', 'Cincinnati'],
    'Virginia':   ['Virginia Beach', 'Richmond'],
    'North Carolina': ['Charlotte', 'Raleigh', 'Greensboro'],
    'Georgia':    ['Atlanta', 'Savannah'],
    'Florida':    ['Miami', 'Orlando', 'Tampa', 'Jacksonville'],
    'Texas':      ['Houston', 'Dallas', 'Austin', 'San Antonio'],
    'Illinois':   ['Chicago', 'Springfield'],
    'Michigan':   ['Detroit', 'Grand Rapids'],
    'Minnesota':  ['Minneapolis', 'Saint Paul'],
    'Missouri':   ['Kansas City', 'Saint Louis'],
    'Kansas':     ['Wichita', 'Overland Park'],
    'Wisconsin':  ['Milwaukee', 'Madison'],
    'Alabama':    ['Birmingham', 'Montgomery'],
    'Arkansas':   ['Little Rock', 'Fayetteville'],
    'Louisiana':  ['New Orleans', 'Baton Rouge'],
    'Mississippi': ['Jackson', 'Gulfport'],
    'Oklahoma':   ['Oklahoma City', 'Tulsa'],
    'Tennessee':  ['Nashville', 'Memphis', 'Knoxville'],
    'Kentucky':   ['Louisville', 'Lexington'],
}

SEGMENTS = ['Consumer', 'Corporate', 'Home Office']
SEGMENT_WEIGHTS = [0.52, 0.30, 0.18]

SHIP_MODES = ['Standard Class', 'Second Class', 'First Class', 'Same Day']
SHIP_MODE_WEIGHTS = [0.59, 0.19, 0.15, 0.07]

SHIP_DAYS_BY_MODE = {
    'Standard Class': (4, 7),
    'Second Class':   (2, 4),
    'First Class':    (1, 2),
    'Same Day':       (0, 0),
}

CATEGORIES = {
    'Furniture': {
        'Bookcases':       {'price_range': (100, 1200), 'base_margin': -0.05, 'discount_freq': 0.40},
        'Chairs':          {'price_range': (80,  1500), 'base_margin':  0.07, 'discount_freq': 0.30},
        'Furnishings':     {'price_range': (10,   400), 'base_margin':  0.10, 'discount_freq': 0.25},
        'Tables':          {'price_range': (200, 2000), 'base_margin': -0.10, 'discount_freq': 0.45},
    },
    'Office Supplies': {
        'Appliances':      {'price_range': (30,   600), 'base_margin':  0.14, 'discount_freq': 0.20},
        'Art':             {'price_range': (3,    100), 'base_margin':  0.12, 'discount_freq': 0.15},
        'Binders':         {'price_range': (1,    300), 'base_margin':  0.06, 'discount_freq': 0.40},
        'Envelopes':       {'price_range': (5,    100), 'base_margin':  0.15, 'discount_freq': 0.10},
        'Fasteners':       {'price_range': (1,     50), 'base_margin':  0.14, 'discount_freq': 0.08},
        'Labels':          {'price_range': (2,     80), 'base_margin':  0.18, 'discount_freq': 0.10},
        'Paper':           {'price_range': (5,    200), 'base_margin':  0.20, 'discount_freq': 0.15},
        'Storage':         {'price_range': (10,   400), 'base_margin':  0.08, 'discount_freq': 0.30},
        'Supplies':        {'price_range': (10,   200), 'base_margin': -0.03, 'discount_freq': 0.35},
    },
    'Technology': {
        'Accessories':     {'price_range': (10,   500), 'base_margin':  0.18, 'discount_freq': 0.20},
        'Copiers':         {'price_range': (300, 6000), 'base_margin':  0.37, 'discount_freq': 0.05},
        'Machines':        {'price_range': (100, 5000), 'base_margin':  0.05, 'discount_freq': 0.15},
        'Phones':          {'price_range': (30,  2000), 'base_margin':  0.20, 'discount_freq': 0.15},
    },
}

# Flatten sub-category list with weights proportional to their category
SUBCAT_LIST = []
SUBCAT_WEIGHTS = []
for cat, subcats in CATEGORIES.items():
    cat_weight = {'Furniture': 0.21, 'Office Supplies': 0.60, 'Technology': 0.19}[cat]
    per_subcat = cat_weight / len(subcats)
    for subcat in subcats:
        SUBCAT_LIST.append((cat, subcat))
        SUBCAT_WEIGHTS.append(per_subcat)

# Normalize weights
SUBCAT_WEIGHTS = np.array(SUBCAT_WEIGHTS)
SUBCAT_WEIGHTS /= SUBCAT_WEIGHTS.sum()

DISCOUNT_VALUES = [0.0, 0.0, 0.0, 0.0, 0.1, 0.1, 0.2, 0.2, 0.2, 0.3, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8]


def random_date(start_year=2014, end_year=2017):
    """Return a random date with Q4-heavy weighting."""
    year  = random.choices(range(start_year, end_year + 1),
                           weights=[0.18, 0.22, 0.27, 0.33])[0]
    # Month with seasonality: Q4 heavier
    month = random.choices(range(1, 13),
                           weights=[0.06, 0.05, 0.09, 0.06, 0.07, 0.07,
                                    0.08, 0.08, 0.09, 0.11, 0.13, 0.11])[0]
    max_day = [31,28,31,30,31,30,31,31,30,31,30,31][month - 1]
    day = random.randint(1, max_day)
    return date(year, month, day)


# ── Build rows ─────────────────────────────────────────────────────────────────
print('Generating %d rows...' % N)

rows = []
order_counter  = 1
customer_pool  = ['C-%05d' % i for i in range(1, 800)]
customer_names = [
    'Aaron Bergman', 'Adam Bellavance', 'Adam Hart', 'Adrian Barton', 'Aimee Bixby',
    'Alan Barnes', 'Alan Haines', 'Alan Hwang', 'Alan Schoenberger', 'Alejandro Ballard',
    'Alejandro Grove', 'Alex Avila', 'Alex Grayson', 'Alex Ruiz', 'Allen Armold',
    'Alyssa Tate', 'Amy Cox', 'Amy Hunt', 'Amy Zwaska', 'Andrew Allen',
    'Andrew Gjertsen', 'Andrew Roberts', 'Andy Reiter', 'Angel Whelply', 'Ann Chong',
    'Anna Andreadi', 'Anna Gayman', 'Anne Pryor', 'Anthony Johnson', 'Anthony OBrien',
    'Arthur Prichep', 'Arthur Wiediger', 'Ashley Common', 'Barbara Frey', 'Barry Weirich',
    'Benjamin Farhat', 'Beth Thompson', 'Bill Donatelli', 'Bill Eplett', 'Bob Takahito',
    'Brad Thomas', 'Brenda Bowman', 'Brendan Dodson', 'Brian Moss', 'Bruce Sherwood',
]

# Generate enough customers to simulate ~793 unique customers
cust_segment = {}
cust_ids = []
for i in range(800):
    cid = 'C-%05d' % (i + 1)
    seg = random.choices(SEGMENTS, weights=SEGMENT_WEIGHTS)[0]
    cust_segment[cid] = seg
    cust_ids.append(cid)

# Product ID pool
product_ids = {}
pid_counter = 1
for cat, subcats in CATEGORIES.items():
    for subcat in subcats:
        for j in range(10):
            key = (cat, subcat, j)
            product_ids[key] = 'P-%s-%03d' % (subcat[:3].upper(), pid_counter)
            pid_counter += 1

def get_product_id(cat, subcat):
    j = random.randint(0, 9)
    return product_ids[(cat, subcat, j)]

product_names_pool = {
    'Bookcases':  ['Sauder 5-Shelf Bookcase', 'Bush Somerset Bookcase', 'Lorell Vertical 5-Shelf', 'O`Sullivan 5-Shelf'],
    'Chairs':     ['HON 5400 Task Chair', 'Global Upholstery Side Chair', 'Safco Executive Chair', 'Bretford Rectangular Table'],
    'Furnishings':['Eldon Expressions Desk', 'Tensor Halogen Desk Lamp', 'Belkin F8E206', 'Artistic Wire Pencil Cup'],
    'Tables':     ['Bevis Round Table', 'Chromcraft Rectangular Conference Table', 'Harbour Creations 66'],
    'Appliances': ['Fellowes PB500 Binding Machine', 'Hoover Stove', 'Acco Heavy Duty Stapler'],
    'Art':        ['Fiskars Scissors', 'Dixon Ticonderoga Pencils', 'Sanford Liquid Highlighter'],
    'Binders':    ['GBC Binding Machine', 'Ibico Presentation Ring Binder', 'Cardinal Easy-Open Binder'],
    'Envelopes':  ['Poly String-Tie Envelopes', 'Staples Mailing Envelopes'],
    'Fasteners':  ['OIC Binder Clips', 'Acco Push Pins', 'Acme Staple Remover'],
    'Labels':     ['Avery Address Labels', 'Avery File Folder Labels'],
    'Paper':      ['Xerox 1967', 'Avery Multipurpose Copy Paper', 'Hammermill Premium Copy Paper'],
    'Storage':    ['Rubbermaid CloseUp', 'Advantus Super Stacker Drawer', 'Smead Hanging File Folders'],
    'Supplies':   ['Dixon Ticonderoga Pencil Sharpener', 'Hoover Commercial ShieldGuard Vacuum'],
    'Accessories':['Logitech Wireless Mouse', 'Kensington USB/PS2 Keyb', 'Plantronics Voyager'],
    'Copiers':    ['Canon PC1060 Copier', 'Hewlett Packard LaserJet 3310', 'Oki B840 Mono Printer'],
    'Machines':   ['Canon imageCLASS', 'Sharp MX-M264N', 'Lexmark MX611dhe'],
    'Phones':     ['Apple iPhone 6', 'Samsung Galaxy S6', 'Motorola Moto G', 'Cisco SPA 501G'],
}


for _ in range(N):
    # Customer
    cid  = random.choice(cust_ids)
    seg  = cust_segment[cid]
    cname_idx = int(cid.split('-')[1]) % len(customer_names)
    cname = customer_names[cname_idx]

    # Region / State / City
    region = random.choices(REGIONS, weights=REGION_WEIGHTS)[0]
    state  = random.choice(STATES_BY_REGION[region])
    city   = random.choice(CITY_BY_STATE.get(state, [state + ' City']))
    postal = str(random.randint(10000, 99999))

    # Product
    idx     = np.random.choice(len(SUBCAT_LIST), p=SUBCAT_WEIGHTS)
    cat, subcat = SUBCAT_LIST[idx]
    info    = CATEGORIES[cat][subcat]
    prod_id = get_product_id(cat, subcat)
    pnames  = product_names_pool.get(subcat, [subcat + ' Product'])
    pname   = random.choice(pnames)

    # Dates
    order_date = random_date()
    ship_mode  = random.choices(SHIP_MODES, weights=SHIP_MODE_WEIGHTS)[0]
    lo, hi     = SHIP_DAYS_BY_MODE[ship_mode]
    ship_lag   = random.randint(lo, hi)
    ship_date  = order_date + timedelta(days=ship_lag)

    # Pricing
    price_lo, price_hi = info['price_range']
    unit_price = round(random.uniform(price_lo, price_hi), 2)
    quantity   = random.choices([1,2,3,4,5,6,7,8,9,10,11,12,13,14],
                                weights=[20,18,15,12,10,8,6,4,3,2,1,1,1,1])[0]
    sales      = round(unit_price * quantity, 2)

    # Discount
    apply_disc = random.random() < info['discount_freq']
    if apply_disc:
        discount = random.choice(DISCOUNT_VALUES[4:])
    else:
        discount = 0.0

    # Profit — base margin adjusted by discount (discounts hurt profit more than proportionally)
    bm = info['base_margin']
    effective_margin = bm - discount * 1.8 + np.random.normal(0, 0.04)
    profit = round(sales * effective_margin, 2)

    # IDs
    order_id    = 'CA-%04d-%06d' % (order_date.year, order_counter)
    order_counter += 1

    rows.append({
        'Row ID':       len(rows) + 1,
        'Order ID':     order_id,
        'Order Date':   order_date.strftime('%d/%m/%Y'),
        'Ship Date':    ship_date.strftime('%d/%m/%Y'),
        'Ship Mode':    ship_mode,
        'Customer ID':  cid,
        'Customer Name': cname,
        'Segment':      seg,
        'Country':      'United States',
        'City':         city,
        'State':        state,
        'Postal Code':  postal,
        'Region':       region,
        'Product ID':   prod_id,
        'Category':     cat,
        'Sub-Category': subcat,
        'Product Name': pname,
        'Sales':        sales,
        'Quantity':     quantity,
        'Discount':     discount,
        'Profit':       profit,
    })

df = pd.DataFrame(rows)

# ── Save ────────────────────────────────────────────────────────────────────────
out_path = 'Sample - Superstore.csv'
df.to_csv(out_path, index=False, encoding='latin-1')

print('Done.')
print('Saved: %s' % out_path)
print('Rows: %d  Columns: %d' % df.shape)
print()
print('Sample head:')
print(df.head(3).to_string())
print()
print('Numeric summary:')
print(df[['Sales','Quantity','Discount','Profit']].describe().round(2).to_string())
