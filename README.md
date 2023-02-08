# Etherscan Labels

Scrapes labels from etherscan website and stores into JSON/CSV.

[Individual Labels (CSV+JSON)](https://github.com/brianleect/etherscan-labels/tree/main/data)

[Combined Labels JSON](https://github.com/brianleect/etherscan-labels/blob/main/combined/combinedLabels.json)

## Setup
1. On the command-line, run the command `pip install -r requirements.txt` while located at folder with code.
1. (Optional) Add ETHERSCAN_USER and ETHERSCAN_PASS to `sample.config.json` and rename to `config.json`
1. Run the script with the command `python main.py`.
1. Login to your etherscan account (Prevents popup/missing data)
1. Press enter in CLI once logged in
1. Proceed to enter either `single` (Retrieve specific label) or `all` (Retrieve ALL labels)
1. If `single`: Follow up with the specific label e.g. `exchange` , `bridge` ....
1. If `all`: Simply let it run (Take about ~1h+ to retrieve all, note that it occassionally crashes as well)
1. Individual JSON and CSV data is dumped into `data` subfolder. 
1. Consolidated JSON label info is dumped into `combined` subfolder.
