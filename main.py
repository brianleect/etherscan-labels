from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager
import pandas as pd
import json
import time
import os.path

# Login to etherscan and auto fill login information if available
def login():
    driver.get('https://etherscan.io/login')
    driver.implicitly_wait(5)
    driver.find_element("id",
        "ContentPlaceHolder1_txtUserName").send_keys(config['ETHERSCAN_USER'])
    driver.find_element(
        "id","ContentPlaceHolder1_txtPassword").send_keys(config['ETHERSCAN_PASS'])

    input("Press enter once logged in")


# Retrieve label information and saves as JSON/CSV
def getLabel(label, type='single'):
    baseUrl = 'https://etherscan.io/accounts/label/{}?subcatid={}&size=100&start={}'
    index = 0  # Initialize start index at 0
    table_list = []

    driver.get(baseUrl.format(label, 'undefined',index))
    driver.implicitly_wait(5)
  
    # Find all elements using driver.find_elements where class matches "nav-link"
    # This is used to find all subcategories
    elems = driver.find_elements("class name","nav-link")
    subcat_id_list = []

    # Loop through elems and append all values to subcat_id_list
    for elem in elems:
        elemVal = elem.get_attribute("val")
        #print(elem.text,elemVal,elem.get_attribute("class")) # Used for debugging elements returned
        if (elemVal is not None): subcat_id_list.append(elemVal)

    print(label,'subcat_values:',subcat_id_list)

    # Bug fix: When there's 0 subcat id found aka ONLY MAIN, we manually add 'undefined' to subcat_id_list
    if (len(subcat_id_list) == 0): subcat_id_list.append('undefined')

    for table_index,subcat_id in enumerate(subcat_id_list):
        index = 0  # Initialize start index at 0

        while (True):
            print('Index:', index,'Subcat:',subcat_id)
            driver.get(baseUrl.format(label, subcat_id,index))
            driver.implicitly_wait(5)

            try:
                # Select relevant table from multiple tables in the page, based on current table index
                curTable = pd.read_html(driver.page_source)[table_index]
                print(curTable)

                # Retrieve all addresses from table
                elems = driver.find_elements("xpath","//a[@href]")
                addressList = []
                addrIndex = len('https://etherscan.io/address/')
                for elem in elems:
                    href = elem.get_attribute("href")
                    if (href.startswith('https://etherscan.io/address/')):
                        addressList.append(href[addrIndex:])
            
                # Replace address column in newTable dataframe with addressList
                curTable['Address'] = addressList
            except Exception as e: 
                print(e)
                print(label, "Skipping label due to error")
                return

            table_list.append(curTable[:-1])  # Remove last item which is just sum
            index += 100

            # If table is less than 100, then we have reached the end
            if (len(curTable.index) != 101):
                break

    df = pd.concat(table_list)  # Combine all dataframes
    df.fillna('', inplace=True)  # Replace NaN as empty string
    df.index = range(len(df.index)) # Fix index for df

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

# Combines all JSON into a single file combinedLabels.json
def combineAllJson():
    combinedJSON = {}

    # iterating over all files
    for files in os.listdir('./data'):
        if files.endswith('json'):
            print(files)  # printing file name of desired extension
            with open('./data/{}'.format(files)) as f:
                dictData = json.load(f)
                for address, nameTag in dictData.items():
                    if address not in combinedJSON:
                        combinedJSON[address] = {'name': nameTag, 'labels': []}
                    combinedJSON[address]['labels'].append(files[:-5])
        else:
            continue

    with open('combined/combinedLabels.json', 'w', encoding='utf-8') as f:
        json.dump(combinedJSON, f, ensure_ascii=True)

# Retrieves all labels from labelcloud and saves as JSON/CSV
def getAllLabels():
    driver.get('https://etherscan.io/labelcloud')
    driver.implicitly_wait(5)

    elems = driver.find_elements("xpath","//a[@href]")
    labels = []
    labelIndex = len('https://etherscan.io/accounts/label/')
    for elem in elems:
        href = elem.get_attribute("href")
        if (href.startswith('https://etherscan.io/accounts/label/')):
            labels.append(href[labelIndex:])

    print(labels)
    print('L:', len(labels))

    for label in labels:
        if (os.path.exists('data/{}.json'.format(label))):
            print(label, 'already exists skipping.')
            continue
        elif label in ignore_list:
            print(label, 'ignored due to large size and irrelevance')
            continue
        getLabel(label, 'all')
        time.sleep(5)  # Give 5s interval to prevent RL

    # Proceed to combine all addresses into single JSON after retrieving all.
    combineAllJson()

# Large size: Eth2/gnsos , Bugged: Liqui , NoData: Remaining labels
ignore_list = ['eth2-depositor', 'gnosis-safe-multisig', 'liqui.io', 'education', 'electronics',
               'flashbots', 'media', 'music', 'network', 'prediction-market', 'real-estate', 'vpn', 'beacon-depositor','uniswap']
with open('config.json', 'r') as f:
    config = json.load(f)

driver = webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()))

login()
retrievalType = input('Enter retrieval type (single/all): ')
if (retrievalType == 'all'):
    getAllLabels()
else:
    singleLabel = input('Enter label of interest: ')
    getLabel(singleLabel)
