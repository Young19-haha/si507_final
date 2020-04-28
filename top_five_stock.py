import requests, json, sqlite3, operator, random, os.path
from os import path
from bs4 import BeautifulSoup
from flask import Flask, render_template, request, url_for
from datetime import datetime, timedelta
import menu_urls
import table_query


menu_links = menu_urls.MENU
baseurl = "http://www.eoddata.com"
watchlist = []
headers = []
menu = []
stock_data = {}
top5 = {}
STOCK_DATA = 'stock_data.json'
HEADERS = 'headers.json'
MENU = 'menu.json'
filename_list = [STOCK_DATA, HEADERS, MENU]

def check_time():
    result = True
    datetimeFormat = '%Y-%m-%d %H:%M:%S.%f'
    time_in_record = ''
    now = datetime.now()
    recorded_time_list = []
    recorded_time = now
    if path.exists('time_record.json'):
        recorded_time_list = read_file('time_record.json')
        # print(recorded_time_list)
        recorded_time = recorded_time_list[-1]
        # print(type(recorded_time))
        recorded_time = datetime.strptime(recorded_time, datetimeFormat) # str to datetime
        # print(type(recorded_time))
        
    timedelta = now - recorded_time 
    if timedelta.days * 24 * 3600 + timedelta.seconds > 3600:
        result = False

    time_in_record = now.strftime(datetimeFormat) # datetime to str
    recorded_time_list.append(time_in_record)
    write_to_file('time_record.json', recorded_time_list)
    return result

def data_process():
    conn = sqlite3.connect('mystock.sqlite')
    cur = conn.cursor()

    cur.execute(table_query.drop_codes)
    cur.execute(table_query.drop_NYSE)
    cur.execute(table_query.create_codes)
    cur.execute(table_query.create_NYSE)

    for code, value in stock_data.items():
        cur.execute(table_query.insert_codes, [code])

    for code, value in stock_data.items():
        NYSE = []
        get_codeId = f"""
            SELECT id from codes
            WHERE code = "{code}";
        """
        cur.execute(get_codeId)
        NYSE = [item[1] for item in value.items()][:3]
        # print(NYSE)
        for row in cur:
            NYSE[0] = row[0]
        # print(NYSE)
        cur.execute(table_query.insert_NYSE, NYSE)

    conn.commit()


def check_file_exist(filename_list):
    # 1. file does not exsit
    # pass
    for filename in filename_list:
        if path.exists(filename):
            return True
        else:
            return False

def write_to_file(filename, mydata):
    with open(filename,'w') as f:
        json.dump(mydata, f)

def read_file(filename):
    with open(filename,'r') as f:
        data = json.load(f)
    return data
    #stock_data = read_file(filename)

# get stock symbol list
def get_symbol_dicts(url):
    """get a list of dictionaries of symbols from url"""
    # new_recorded_time = datetime.now()
    # print(new_recorded_time)
    # time_record.recorded_time.append(new_recorded_time)
    # print(time_record.recorded_time)
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

# def index2(yesterday_volume, today_volume):
#     """higher index2 for more buyers; if >3 then there's something happened"""
#     try:
#         return (today_volume - yesterday_volume) / yesterday_volume
#     except ZeroDivisionError:
#         return 0

def calculate_():
    """return a dict of dicts of modified data with index1"""
    modified_data = {}
    for code, item_data in stock_data.items():
        # print(item_data)
        # print(headers)
        condition1 = index1(item_data['High'], item_data['Low'], item_data['Close'])
        modified_data[code] = condition1
        # modified_data['condition2'] = condition2
    return modified_data

def today_top5():
    """a list of dictionary of suggested stock with code, name, url 
    for today's top 5 stock you most want pay attention"""
    prepared_data = calculate_()
    # print(prepared_data)
    sorted_data = dict(sorted(prepared_data.items(), key=operator.itemgetter(1),reverse=True))
    # print(sorted_data)
    sorted_key = [item[0] for item in sorted_data.items()]
    # print(sorted_key)
    mytop = {}
    for key in sorted_key:
        if sorted_data[key] >= 1:
            mytop[key] = stock_data[key]
    # for i in range(5):
    #     top5[sorted_key[i]] = stock_data[sorted_key[i]]
    for i in range(5):
        top_key, top_value = random.choice(list(mytop.items()))
        top5[top_key] = top_value
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
            with open('watchlist.json','w') as f:
                json.dump(watchlist, f)
    return render_template('response.html', watchlist=watchlist, menu=menu)

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
                            condition=condition,
                            menu=menu)

@app.route('/watchlist.html')
def watch_list():
    return render_template('watchlist.html',
                            watchlist=watchlist,
                            menu=menu)



if __name__== '__main__':
    if check_file_exist(filename_list) is False or check_time() is False:
        # for filename in filename_list:
        #     os.remove(filename)
        headers, menu, stock_data = get_stock_symbol_menu()
        write_to_file(HEADERS, headers)
        write_to_file(MENU, menu)
        write_to_file(STOCK_DATA, stock_data)
    else:
        headers = read_file(HEADERS)
        menu = read_file(MENU)
        stock_data = read_file(STOCK_DATA)

    top5 = today_top5()
    data_process()
    app.run(debug=True)
    # pass