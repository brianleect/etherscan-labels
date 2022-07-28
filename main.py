from selenium import webdriver
import pandas as pd
import json

driver = webdriver.Chrome()
with open('config.json', 'r') as f:
    config = json.load(f)

# Login to etherscan and auto fill login information if available
def login():
    driver.get('https://etherscan.io/login')
    driver.implicitly_wait(5)
    driver.find_element_by_id(
        "ContentPlaceHolder1_txtUserName").send_keys(config['ETHERSCAN_USER'])
    driver.find_element_by_id(
        "ContentPlaceHolder1_txtPassword").send_keys(config['ETHERSCAN_PASS'])

    input("Press enter once logged in")


# Retrieve label information and saves to 
def getLabel(label):
    baseUrl = 'https://etherscan.io/accounts/label/{}?subcatid=0&size=100&start={}'
    index = 0  # Initialize start index at 0
    table_list = []
    while (True):
        print('Index:', index)
        driver.get(baseUrl.format(label, index))
        driver.implicitly_wait(5)
        newTable = pd.read_html(driver.page_source)[0]
        table_list.append(newTable[:-1])  # Remove last item which is just sum
        index += 100
        if (len(newTable.index) != 101):
            break

    df = pd.concat(table_list)  # Combine all dataframes
    df.fillna('', inplace=True)  # Replace NaN as empty string

    # Prints length and save as a csv
    print('Df length:', len(df.index))
    df.to_csv('data/{}.csv'.format(label))

    # Save as json object with mapping address:nameTag
    addressNameDict = dict([(address, nameTag)
                           for address, nameTag in zip(df.Address, df['Name Tag'])])
    with open('data/{}.json'.format(label), 'w', encoding='utf-8') as f:
        json.dump(addressNameDict, f, ensure_ascii=True)

    endOrContinue = input(
        'Type "exit" end to end or "label" of interest to continue')
    if (endOrContinue == 'exit'):
        driver.close()
    else:
        getLabel(endOrContinue)


login()
startInput = input('Enter label of interest: ')
getLabel(startInput)
