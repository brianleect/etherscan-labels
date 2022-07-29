from selenium import webdriver
import pandas as pd
import json
import time
import os.path

# Login to etherscan and auto fill login information if available
def login():
    driver.get('https://etherscan.io/login')
    driver.implicitly_wait(5)
    driver.find_element_by_id(
        "ContentPlaceHolder1_txtUserName").send_keys(config['ETHERSCAN_USER'])
    driver.find_element_by_id(
        "ContentPlaceHolder1_txtPassword").send_keys(config['ETHERSCAN_PASS'])

    input("Press enter once logged in")


# Retrieve label information and saves as JSON/CSV
def getLabel(label, type='single'):
    baseUrl = 'https://etherscan.io/accounts/label/{}?subcatid=0&size=100&start={}'
    index = 0  # Initialize start index at 0
    table_list = []
    while (True):
        print('Index:', index)
        driver.get(baseUrl.format(label, index))
        driver.implicitly_wait(5)
        try:
            newTable = pd.read_html(driver.page_source)[0]
        except ImportError:
            print(label, "Skipping label due to error")
            return
        table_list.append(newTable[:-1])  # Remove last item which is just sum
        index += 100
        if (len(newTable.index) != 101):
            break

    df = pd.concat(table_list)  # Combine all dataframes
    df.fillna('', inplace=True)  # Replace NaN as empty string

    # Prints length and save as a csv
    print(label, 'Df length:', len(df.index))
    df.to_csv('data/{}.csv'.format(label))

    # Save as json object with mapping address:nameTag
    addressNameDict = dict([(address, nameTag)
                           for address, nameTag in zip(df.Address, df['Name Tag'])])
    with open('data/{}.json'.format(label), 'w', encoding='utf-8') as f:
        json.dump(addressNameDict, f, ensure_ascii=True)

    if (type == 'single'):
        endOrContinue = input(
            'Type "exit" end to end or "label" of interest to continue')
        if (endOrContinue == 'exit'):
            driver.close()
        else:
            getLabel(endOrContinue)


# Retrieves all labels from labelcloud and saves as JSON/CSV
def getAllLabels():
    driver.get('https://etherscan.io/labelcloud')
    driver.implicitly_wait(5)

    elems = driver.find_elements_by_xpath("//a[@href]")
    labels = []
    labelIndex = len('https://etherscan.io/accounts/label/')
    for elem in elems:
        href = elem.get_attribute("href")
        if (href.startswith('https://etherscan.io/accounts/label/')):
            labels.append(href[labelIndex:])

    print(labels)
    print('L:', len(labels))

    for label in labels:
        if (os.path.exists('data/{}.csv'.format(label))):
            print(label, 'already exists skipping.')
            continue
        elif label in ignore_list:
            print(label,'ignored due to large size and irrelevance')
            continue
        getLabel(label, 'all')
        time.sleep(5)  # Give 5s interval to prevent RL


ignore_list = ['eth2-depositor', 'gnosis-safe-multisig']
with open('config.json', 'r') as f:
    config = json.load(f)
driver = webdriver.Chrome()

login()
retrievalType = input('Enter retrieval type (single/all): ')
if (retrievalType == 'all'):
    getAllLabels()
else:
    singleLabel = input('Enter label of interest: ')
    getLabel(singleLabel)
