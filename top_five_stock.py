import requests
import json
from bs4 import BeautifulSoup
from flask import Flask, render_template, request, url_for
import menu_urls
import operator

menu_links = menu_urls.MENU
baseurl = "http://www.eoddata.com"
watchlist = []

# get stock symbol list
def get_symbol_dicts(url):
    """get a list of dictionaries of symbols from url"""
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')
    table = soup.find('table', class_="quotes")
    table_rows = table.find_all('tr')                            # get all rows in the table
    headers = [item.text.strip() for item in table_rows[0]][:-1] # get variable name for the table
    symbol_rows = table_rows[1:]                                 # get data from the table

    data_list = []
    for row in symbol_rows:
        mydict = {}
        mydict[headers[0]] = row.find_all('td')[0].text.strip() # code
        mydict[headers[1]] = row.find_all('td')[1].text.strip() # name
        mydict['url'] = baseurl + row.find('a')['href']         # url
        mydict[headers[2]] = float(row.find_all('td')[2].text.strip().replace(',','')) if ',' in row.find_all('td')[2].text.strip() else float(row.find_all('td')[2].text.strip()) # high
        mydict[headers[3]] = float(row.find_all('td')[3].text.strip().replace(',','')) if ',' in row.find_all('td')[3].text.strip() else float(row.find_all('td')[3].text.strip()) # low
        mydict[headers[4]] = float(row.find_all('td')[4].text.strip().replace(',','')) if ',' in row.find_all('td')[4].text.strip() else float(row.find_all('td')[4].text.strip()) # close
        mydict[headers[5]] = float(row.find_all('td')[5].text.strip().replace(',','')) if ',' in row.find_all('td')[5].text.strip() else float(row.find_all('td')[5].text.strip()) # volume
        mydict[headers[6]] = float(row.find_all('td')[6].text.strip().replace(',','')) if ',' in row.find_all('td')[6].text.strip() else float(row.find_all('td')[6].text.strip()) # change
        # print(mydict)
        data_list.append(mydict)
    return headers, data_list

def get_stock_symbol_menu():
    """get menu list & get stock data dict"""
    menu = []
    stock_data = {}
    for url in menu_links:
        headers, data_list = get_symbol_dicts(url)
        for item in data_list:
            stock_data.update({item['Code']:item})
    menu = [item[0] for item in stock_data.items()]
    headers = [item[0] for item in stock_data[menu[0]].items()]
    return headers, menu, stock_data

def index1(high, low, close):
    """higher index1 for more buyers"""
    try:
        return (close - low) / (high - low)
    except ZeroDivisionError:
        return 0
    

def index2(yesterday_volume, today_volume):
    """higher index2 for more buyers; if >3 then there's something happened"""
    try:
        return (today_volume - yesterday_volume) / yesterday_volume
    except ZeroDivisionError:
        return 0
    

def assign_data(mydict, headers):
    mylist = [item[1] for item in mydict.items()] # a list of values, 
    #its length supposed to be the same as headers
    my_data = {}
    for i in range(len(headers)):
        # print(detail_headers[i])
        # print(mylist[i])
        value = mylist[i]
        # my_data[headers[i]] = float(value.replace(',','')) if value.isnumeric() else value
        # my_data[headers[i]] = convert_str_to_num(value)
        my_data[headers[i]] = value
    # volume_list = my_data['Volume'].split(',')
    # volume = 0
    # if len(volume_list) == 3:
    #     volume = volume_list[0] * 1000000 + volume_list[1] * 1000 + volume_list[2]
    # elif len(volume_list) == 2:
    #     volume = volume_list[0] * 1000 + volume_list[1]
    # elif len(volume_list) == 1:
    #     volume = volume_list[0]
    # my_data['Volume'] = volume
    return my_data

def calculate_():
    """return a dict of dicts of modified data with index1"""
    # # get detail data fro each stock
    # response = requests.get(url)
    # soup = BeautifulSoup(response.text, 'html.parser')
    # table = soup.find('table', class_="quotes")
    # table_rows = table.find_all('tr')                                   # get all rows in the table
    # detail_headers = [item.text.strip() for item in table_rows[0]][:-1] # get variable name for the table
    # # print(detail_headers)
    # data_rows = table_rows[1:3]                                         # get data from the table
    # # print(data_rows)

    # # for item in data_rows[0].find_all('td')[0].text.strip():
    # #     for i in range(len(headers)):
    # #         today_data[headers[i]] = item
    # yesterday_data = assign_data(data_rows[1].find_all('td'), detail_headers)
    # # for item in data_rows[1].find_all('td')[0].text.strip():
    # #     for i in range(len(headers)):
    # #         today_data[headers[i]] = item
    # condition1 = index1(today_data['High'], today_data['Low'], today_data['Close'])
    # condition2 = index2(yesterday_data['Volume'], today_data['Volume'])
    modified_data = {}
    for code, item_data in stock_data.items():
        today_data = assign_data(item_data, headers)
        # print(today_data)
        condition1 = index1(today_data['High'], today_data['Low'], today_data['Close'])
        modified_data[code] = condition1
    # modified_data['condition2'] = condition2
    return modified_data



def today_top5():
    """a list of dictionary of suggested stock with code, name, url 
    for today's top 5 stock you most want pay attention"""
    # pass
    # prepared_data = {}
    # for code, stock in base_data.items():
    #     prepared_data[code] = calculate_(stock['url'])
    # items = prepared_data.items()
    # sorted_data = sorted(items, key=lambda key_value: key_value[1]["condition1"], reverse=True)
    max_index1 = 0.0
    # max_index2 = 0.0
    # top_code = []
    # for code, indices in prepared_data.items():
    #     if indices['condition2'] > 3:
    #         top_code.append(code)
    prepared_data = calculate_()
    top5 = {}
    # for code, value in prepared_data.items():
    #     if value.items()[1] > max_index1:
    #     top5[code] = stock_data[code]
    sorted_data = dict(sorted(prepared_data.items(), key=operator.itemgetter(1),reverse=True))
    sorted_key = [item[0] for item in sorted_data.items()]
    for i in range(5):
        top5[sorted_key[i]] = stock_data[sorted_key[i]]
    return top5



app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html',
                            headers=headers,
                            menu=menu,
                            top5=top5)

@app.route('/index.html')
def homepage():
    return render_template('index.html',
                            headers=headers,
                            menu=menu,
                            top5=top5)

@app.route('/add_to_watchlist', methods=['GET', 'POST']) # response
def add_to_watchlist():
    name = ''
    for code in menu:
        if code in request.form and code not in [item['Code'] for item in watchlist]:
            # name = request.args[code]
            watchlist.append(stock_data[code])
    return render_template('response.html', watchlist=watchlist)

@app.route('/search_result', methods=['GET', 'POST']) # search response
def search_result():
    search = request.args['search']
    condition = False
    for item in menu:
        if search.upper() == item:
            result = stock_data[item] # {code, name, url}
            condition = True
    return render_template('search_response.html',
                            result=result,
                            condition=condition)

@app.route('/watchlist.html')
def watch_list():
    return render_template('watchlist.html',
                            watchlist=watchlist)



if __name__== '__main__':
    headers, menu, stock_data = get_stock_symbol_menu() # get menu list of dictionary with code, name, and url
    # print(headers)
    # print(stock_data[menu[0]])
    # with open('menu.json','w') as f:
        # f = json.dumps(menu)
    # top5 = {'A':{"Code":"A","Name":"AAAAAA",'High':70,'Low':50,'Close':10,'Volumne':10000,'Change':155}} # get top 5 stock list of dictionary with code, name, and url
    top5 = today_top5() 
    app.run(debug=True)
    # pass