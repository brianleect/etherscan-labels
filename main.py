import traceback
from selenium import webdriver
import undetected_chromedriver as uc
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager
import pandas as pd
import json
import time
import os.path

# Scan site mapping from chain to __scan url
CHAIN_MAP = {
    "eth": {"baseUrl": "https://etherscan.io", "savePath": "./data/etherscan/"},
    "bsc": {"baseUrl": "https://bscscan.com", "savePath": "./data/bscscan/"},
    "poly": {"baseUrl": "https://polygonscan.com", "savePath": "./data/polygonscan/"},
    "opt": {
        "baseUrl": "https://optimistic.etherscan.io",
        "savePath": "./data/optimism/",
    },
    "arb": {"baseUrl": "https://arbiscan.io", "savePath": "./data/arbiscan/"},
    "ftm": {"baseUrl": "https://ftmscan.com", "savePath": "./data/ftmscan/"},
    "avax": {"baseUrl": "https://snowtrace.io", "savePath": "./data/avalanche/"},
}

# Combine and split all chainMap keys by '/'
ALL_CHAINS = "/".join(CHAIN_MAP.keys())


# Login to etherscan and auto fill login information if available
def login(config):
    driver.get("{}/login".format(base_url))
    driver.implicitly_wait(5)
    driver.find_element("id", "ContentPlaceHolder1_txtUserName").send_keys(
        config["ETHERSCAN_USER"]
    )
    driver.find_element("id", "ContentPlaceHolder1_txtPassword").send_keys(
        config["ETHERSCAN_PASS"]
    )

    input("Press enter once logged in")


# Retrieve label information and saves as JSON/CSV
def get_label(label, label_type="account", input_type="single"):
    if "eth" not in base_url:
        get_label_old_format(label, label_type=label_type, input_type=input_type)
        return

    base_url_label = base_url + "/{}s/label/{}?subcatid={}&size=100&start={}"
    index = 0  # Initialize start index at 0
    table_list = []

    url = base_url_label.format(label_type, label, "undefined", index)
    print(f"getting {url}")
    driver.get(url)
    driver.implicitly_wait(5)

    # Find all elements using driver.find_elements where class matches "nav-link"
    # This is used to find all subcategories
    elems = driver.find_elements("class name", "nav-link")
    subcat_id_list = []

    # Loop through elems and append all values to subcat_id_list
    for elem in elems:
        elem_val = elem.get_attribute("val")
        # print(elem.text,elemVal,elem.get_attribute("class")) # Used for debugging elements returned
        if elem_val is not None:
            subcat_id_list.append(elem_val)

    print(label, "subcat_values:", subcat_id_list)

    # Bug fix: When there's 0 subcat id found aka ONLY MAIN, we manually add 'undefined' to subcat_id_list
    if len(subcat_id_list) == 0:
        subcat_id_list.append("undefined")

    addr_col_name = (
        "Address" if label_type == "account" else "Contract Address"
    )  # when "token"
    # use td to limit the column, avoiding that the address_list being longer than the table
    td_index = 1 if label_type == "account" else 2  # when "token"

    for table_index, subcat_id in enumerate(subcat_id_list):
        index = 0  # Initialize start index at 0
        driver.implicitly_wait(5)
        driver.get(base_url_label.format(label_type, label, subcat_id, index))
        time.sleep(20)  # TODO: allow customization by args

        while True:
            print("Index:", index, "Subcat:", subcat_id)

            try:
                # Select relevant table from multiple tables in the page, based on current table index
                cur_table = pd.read_html(driver.page_source)[table_index]
                print(cur_table)
                if (
                    pd.isnull(cur_table[addr_col_name].iloc[-1])
                    or cur_table[addr_col_name].iloc[-1]
                    == "No Token Contracts found for the address."
                ):
                    print("remove last row")
                    cur_table = cur_table[:-1]

                # Retrieve all addresses from table
                elems = driver.find_elements(
                    "xpath",
                    f'//div[contains(@class, "active")]//tbody//td[{td_index}]//a[@href]',
                )
                address_list = (
                    set()
                )  # avoid `class = "tab-pane fade"` which dup the list
                addr_index = len(base_url + "/address/")
                for elem in elems:
                    href = elem.get_attribute("href")
                    if href.startswith(base_url + "/address/"):
                        address_list.add(href[addr_index:])

                if len(cur_table.index) > 0 and len(address_list) == 0:
                    print(
                        f"failed to load addresses from href ({len(address_list)}/{len(cur_table.index)}), retry parsing..."
                    )
                    continue

                # Quickfix: Optimism uses etherscan subcat style but differing address format
                if targetChain == "eth":
                    # Replace address column in newTable dataframe with addressList
                    if label_type == "account":
                        cur_table["Address"] = list(address_list)
                    elif label_type == "token":
                        cur_table["Contract Address"] = list(address_list)
            except Exception as e:
                print(e)
                traceback.print_exc()
                print(label, "Skipping label due to error")
                return

            table_list.append(cur_table)

            # If table is less than 100, then we have reached the end
            if len(cur_table.index) == 100:
                while True:
                    next_icon_elems = driver.find_elements("class name", "fa-chevron-right")
                    try:
                        next_icon_elems[0].click()
                        time.sleep(20) # beacon-depositor require longer # TODO: allow customization by args
                        break
                    except Exception as e:
                        print("failed on clicking next page button", e)
                        traceback.print_exc()
            else:
                break

    df = pd.concat(table_list)  # Combine all dataframes
    df.fillna("", inplace=True)  # Replace NaN as empty string
    df.index = range(len(df.index))  # Fix index for df

    # Prints length and save as a csv
    print(label, "Df length:", len(df.index))
    df.to_csv(savePath + "{}s/{}.csv".format(label_type, label))

    # Save as json object with mapping address:nameTag
    if label_type == "account":
        addressNameDict = dict(
            [
                (address, nameTag)
                for address, nameTag in zip(df["Address"], df["Name Tag"])
            ]
        )
    if label_type == "token":
        addressNameDict = dict(
            [
                (address, nameTag)
                for address, nameTag in zip(df["Contract Address"], df["Token Name"])
            ]
        )
    with open(
        savePath + "{}s/{}.json".format(label_type, label), "w", encoding="utf-8"
    ) as f:
        json.dump(addressNameDict, f, ensure_ascii=True)


def get_label_old_format(label, label_type="account", input_type="single"):
    print("Getting label old format", label)
    base_url_label = base_url + "/{}s/label/{}?subcatid=undefined&size=100&start={}"
    index = 0  # Initialize start index at 0
    table_list = []
    time.sleep(20)

    while True:
        try:
            print("Index:", index)
            driver.get(base_url_label.format(label_type, label, index))
            driver.implicitly_wait(1)
            curTable = pd.read_html(driver.page_source)[0]
        except Exception as e:
            print(e)
            traceback.print_exc()
            print(label, "Skipping label due to error")

            # Save empty CSV and JSON
            empty_df = pd.DataFrame()
            empty_df.to_csv(savePath + "{}s/empty/{}.csv".format(label_type, label))

            empty_dict = {}
            with open(
                savePath + "{}s/empty/{}.json".format(label_type, label),
                "w",
                encoding="utf-8",
            ) as f:
                json.dump(empty_dict, f, ensure_ascii=True)
            return

        table_list.append(curTable)

        index += 100
        if len(curTable.index) != 100:
            break

    df = pd.concat(table_list)  # Combine all dataframes
    df.fillna("", inplace=True)  # Replace NaN as empty string
    df.index = range(len(df.index))  # Fix index for df

    # Prints length and save as a csv
    print(label, "Df length:", len(df.index))
    df.to_csv(savePath + "{}s/{}.csv".format(label_type, label))

    # Save as json object with mapping address:nameTag
    if label_type == "account":
        address_name_dict = dict(
            [
                (address, name_tag)
                for address, name_tag in zip(df["Address"], df["Name Tag"])
            ]
        )
    if label_type == "token":
        address_name_dict = dict(
            [
                (address, name_tag)
                for address, name_tag in zip(df["Contract Address"], df["Token Name"])
            ]
        )
    with open(
        savePath + "{}s/{}.json".format(label_type, label), "w", encoding="utf-8"
    ) as f:
        json.dump(address_name_dict, f, ensure_ascii=True)

    if input_type == "single":
        endOrContinue = input(
            'Type "exit" end to end or "label" of interest to continue'
        )
        if endOrContinue == "exit":
            driver.close()
        else:
            get_label_old_format(endOrContinue, label_type=label_type)


# Combines all JSON into a single file combinedLabels.json
def combine_all_json():
    combined_account_json = {}

    # iterating over all files
    for files in os.listdir(savePath + "accounts"):
        if files.endswith("json"):
            print(files)  # printing file name of desired extension
            with open(savePath + "accounts/{}".format(files)) as f:
                dict_data = json.load(f)
                for address, name_tag in dict_data.items():
                    if address not in combined_account_json:
                        combined_account_json[address] = {
                            "name": name_tag,
                            "labels": [],
                        }
                    combined_account_json[address]["labels"].append(files[:-5])
        else:
            continue

    combined_token_json = {}
    for files in os.listdir(savePath + "tokens"):
        if files.endswith("json"):
            print(files)  # printing file name of desired extension
            with open(savePath + "tokens/{}".format(files)) as f:
                dict_data = json.load(f)
                for address, name_tag in dict_data.items():
                    if address not in combined_token_json:
                        combined_token_json[address] = {"name": name_tag, "labels": []}
                    combined_token_json[address]["labels"].append(files[:-5])
        else:
            continue

    combined_all_json = {
        key: {**combined_account_json.get(key, {}), **combined_token_json.get(key, {})}
        for key in set(
            list(combined_account_json.keys()) + list(combined_token_json.keys())
        )
    }

    with open(
        savePath + "combined/combinedAccountLabels.json", "w", encoding="utf-8"
    ) as f:
        json.dump(combined_account_json, f, ensure_ascii=True)
    with open(
        savePath + "combined/combinedTokenLabels.json", "w", encoding="utf-8"
    ) as f:
        json.dump(combined_token_json, f, ensure_ascii=True)
    with open(savePath + "combined/combinedAllLabels.json", "w", encoding="utf-8") as f:
        json.dump(combined_all_json, f, ensure_ascii=True)


# Retrieves all labels from labelcloud and saves as JSON/CSV
def get_all_labels(all_type):
    all_type = all_type.lower()

    driver.get(base_url + "/labelcloud")
    driver.implicitly_wait(5)

    elems = driver.find_elements("xpath", "//a[@href]")
    labels = []
    accountsIndex = len(base_url + "/accounts/label/")
    tokensIndex = len(base_url + "/tokens/label/")
    for elem in elems:
        href = elem.get_attribute("href")
        if href.startswith(base_url + "/accounts/label/"):
            label = href[accountsIndex:]
            labels.append(label.strip("+"))
        elif href.startswith(base_url + "/tokens/label/"):
            label = href[tokensIndex:]
            labels.append(label.strip("+"))  # fix `remittance+`

    print(labels)

    # Remove duplicates from array labels
    labels = list(dict.fromkeys(labels))
    print("L:", len(labels))

    def _get_all_accounts():
        for label in labels:
            if os.path.exists(
                savePath + "accounts/{}.json".format(label)
            ) or os.path.exists(savePath + "accounts/empty/{}.json".format(label)):
                print(label, "'s account labels already exist, skipping.")
                continue

            get_label(label, "account", "all")
            time.sleep(20)  # Give interval to prevent RL

    def _get_all_tokens():
        for label in labels:
            if os.path.exists(
                savePath + "tokens/{}.json".format(label)
            ) or os.path.exists(savePath + "tokens/empty/{}.json".format(label)):
                print(label, "'s token labels already exist, skipping.")
                continue
            # elif label in ignore_list:
            #     print(label, 'ignored due to large size and irrelevance')
            #     continue

            get_label(label, "token", "all")
            time.sleep(20)  # Give 1s interval to prevent RL

    if all_type == "all":
        _get_all_accounts()
        _get_all_tokens()
    elif all_type.startswith("account"):
        _get_all_accounts()
    elif all_type.startswith("token"):
        _get_all_tokens()
    else:
        raise Exception("unknown get all type: " + all_type)


if __name__ == "__main__":
    with open("config.json", "r") as f:
        config = json.load(f)

    targetChain = input("Enter scan site of interest ({}): ".format(ALL_CHAINS))

    if targetChain not in CHAIN_MAP:
        print("Invalid chain input, exiting, please try again with a valid option")
        exit()
    else:
        base_url = CHAIN_MAP[targetChain]["baseUrl"]
        savePath = CHAIN_MAP[targetChain]["savePath"]

    #     driver = webdriver.Chrome(service=ChromeService(
    #         ChromeDriverManager().install()))

    driver = uc.Chrome(service=ChromeService(ChromeDriverManager().install()))

    login(config)

    while True:
        retrieval_type = input("Enter retrieval type (single/all): ")
        if retrieval_type == "all":
            all_type = input("Enter get all address type (account/token/all): ")
            get_all_labels(all_type)
            # Proceed to combine all addresses into single JSON after retrieving all.
            combine_all_json()
        elif retrieval_type == "single":
            singleLabel = input("Enter label of interest: ")
            get_label(singleLabel, "account")
            get_label(singleLabel, "token")
        elif retrieval_type == "exit":
            driver.close()
