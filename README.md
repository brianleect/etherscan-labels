# Etherscan Labels

Scrapes labels from etherscan website and stores into JSON/CSV.

[Label Data dump](https://github.com/brianleect/etherscan-labels/tree/main/data)

## Setup
1. On the command-line, run the command `pip install -r requirements.txt` while located at folder with code.
1. (Required) Setup selenium by [downloading relevant drivers and adding to path](https://www.selenium.dev/documentation/webdriver/getting_started/install_drivers/)
1. (Optional) Add ETHERSCAN_USER and ETHERSCAN_PASS to `sample.config.json` and rename to `config.json`
1. Run the script with the command `python main.py`.
1. Login to your etherscan account (Prevents popup/missing data)
1. Press enter in CLI once logged in
1. Proceed to enter either "single" or "all" depending on whether you wish to retrieve a specific label or ALL
1. If 'single': Follow up with the specific label e.g. 'exchange' , 'bridge' ....
1. If 'all': Simply let it run (Take about ~1h+ to retrieve all)
1. JSON and CSV data is dumped into data folder.
