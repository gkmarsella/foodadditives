from flask import Flask, render_template, request, redirect, url_for, jsonify
from flask_modus import Modus
from flask_sqlalchemy import SQLAlchemy
import sys
import os
import requests
import urllib.request
import json
import re
from add_details import add_details



app = Flask(__name__)
api = Modus(app)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgres://localhost/additive-db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

usda_key = app.config['USDA_KEY'] = os.environ.get('USDA_KEY')

mashape_key = app.config['MASHAPE_KEY'] = os.environ.get('MASHAPE_KEY')

walmart_key = app.config['WALMART_KEY'] = os.environ.get('WALMART_KEY')

@app.route('/', methods=[ "GET"])
def search():
    return render_template("search.html")

@app.route('/references', methods=[ "GET"])
def references():
    return render_template("references.html")
    
@app.route('/about', methods=["GET"])
def about():
    return render_template("about.html")

@app.route('/results', methods=["GET", "POST"])
def results():


    # searching for foods
    search_dict = {
        "q": request.args.get('search-food').lower(), 
        "sort":"n", 
        "max": "50",
        "api_key": usda_key,
        "format": "json",
    }

    try:
        search_response = requests.get("https://api.nal.usda.gov/ndb/search/", params=search_dict)
        search = search_response.json()
        product_list = search['list']['item']
    except (json.decoder.JSONDecodeError, KeyError) as e:
        no_results = request.args.get('search-food').lower()
        return render_template("400.html", no_results=no_results)


    # grabbing all product names


    products = []
    for i in product_list:
        products.append(i['name'])

    # counter for product_obj
    prodlength = len(products)

    ndbno_list = []
    for i in product_list:
        ndbno_list.append(i['ndbno'])

    ingredients = []
    for i in ndbno_list:
        try:
            ingredients.append(ingredient_lookup(i)['report']['food']['ing']['desc'])
        except (json.decoder.JSONDecodeError, KeyError) as e:
            ingredients.append("No ingredients found")
    
    counter = 0
    product_obj = {}
    # setting key object pairs of foods upc to its ingredients for lookup
    upc_ingredients = {}
    while prodlength > counter:
        for i in products:
            product_obj[i] = ingredients[counter]
            upc_ingredients[i] = ingredients[counter]
            counter = counter+1


    # putting names and unique codes in an object

    product_ndbno = {}
    for i in product_list:
        checkGTIN = re.search(r"\bGTIN\b", i['name'])
        checkUPC = re.search(r"\bUPC\b", i['name'])
        if checkGTIN:
            product_ndbno[i['name'][:-22]] = i['ndbno']
        if checkUPC:
            product_ndbno[i['name'][:-19]] = i['ndbno']

    return render_template("results.html", search=search, product_obj=product_obj, ingredients=ingredients, product_ndbno=product_ndbno)


@app.route('/get_ingredients', methods=["POST"])
def get_ingredients():
    ndbno = request.json
    search_ndbno_dict = {
        "ndbno": ndbno,
        "type": "f",
        "api_key": usda_key,
        "format": "json",
    }
    search_ndbno_response = requests.get("https://api.nal.usda.gov/ndb/reports", params=search_ndbno_dict)
    search_ndbno = search_ndbno_response.json()

# searching through added additives
    additives = []
    for ingredient in add_details:
        if ingredient.upper() in search_ndbno['report']['food']['ing']['desc']:
            additives.append(ingredient)

    additive_information = {}
    for i in additives:
        if i.upper() in add_details:
            additive_information[i] = add_details[i.upper()]

    return jsonify({'search_ndbno': search_ndbno, 'additives': additives, 'additive_information': additive_information})



def ingredient_lookup(ndbno):
    search_ndbno_dict = {
        "ndbno": ndbno,
        "type": "f",
        "api_key": usda_key,
        "format": "json",
    }
    search_ndbno_response = requests.get("https://api.nal.usda.gov/ndb/reports", params=search_ndbno_dict)
    search_ndbno = search_ndbno_response.json()
    return search_ndbno

# def get_additives():
#     response = requests.get("https://vx-e-additives.p.mashape.com/additives?locale=en&order=asc&sort=last_update",
#       headers={
#         "X-Mashape-Key": mashape_key,
#         "Accept": "application/json"
#       }
#     )

#     return response.json()

def additive_function(code):
    response = requests.get("https://vx-e-additives.p.mashape.com/additives/951?locale=en",
      headers={
        "X-Mashape-Key": mashape_key,
        "Accept": "application/json"
      }
    )

    return response.json()

def additive_lookup(code):
    response = requests.get('https://vx-e-additives.p.mashape.com/additives/' + code,
        headers={
        "X-Mashape-Key": mashape_key,
        "Accept": "application/json"
        }
    )



def upc_lookup(upcode):
    response = requests.get("http://api.walmartlabs.com/v1/items?",
        headers={
            "apiKey": walmart_key,
            "format": "json",
            "upc": upcode
        }
    )



    return response.json()   


@app.route('/signup')
def signup():
    return render_template('signup.html')
    

if os.environ.get('ENV') == 'production':
    debug = False
else:
    debug = True

if __name__ == '__main__':
    app.run(debug=debug,port=3000)
