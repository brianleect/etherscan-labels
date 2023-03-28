# EVM Labels

Scrapes labels from etherscan, bscscan & polygonscan, arbitrium, fantom, avalanche website and stores into JSON/CSV.
---

| Chain | Site | Label Count | Status | Last scraped |
|-------|------|-------------|--------|--------------|
| [ETH](https://github.com/brianleect/etherscan-labels/tree/main/data/etherscan) | [https://etherscan.io](https://etherscan.io) | [27352](https://github.com/brianleect/etherscan-labels/tree/main/./data/etherscan/combined/combinedAllLabels.json) | 🔴 Blocked by scraping bug | 23/2/2023 |
| [BSC](https://github.com/brianleect/etherscan-labels/tree/main/data/bscscan) | [https://bscscan.com](https://bscscan.com) | [6726](https://github.com/brianleect/etherscan-labels/tree/main/./data/bscscan/combined/combinedAllLabels.json) | ✅ ok | 26/3/2023 |
| [POLY](https://github.com/brianleect/etherscan-labels/tree/main/data/polygonscan) | [https://polygonscan.com](https://polygonscan.com) | [4997](https://github.com/brianleect/etherscan-labels/tree/main/./data/polygonscan/combined/combinedAllLabels.json) | ✅ ok | 26/3/2023 |
| [OPT](https://github.com/brianleect/etherscan-labels/tree/main/data/optimism) | [https://optimistic.etherscan.io](https://optimistic.etherscan.io) | [546](https://github.com/brianleect/etherscan-labels/tree/main/./data/optimism/combined/combinedAllLabels.json) |✅ ok | 29/3/2023 |
| [ARB](https://github.com/brianleect/etherscan-labels/tree/main/data/arbiscan) | [https://arbiscan.io](https://arbiscan.io) | [837](https://github.com/brianleect/etherscan-labels/tree/main/./data/arbiscan/combined/combinedAllLabels.json) | ✅ ok | 26/3/2023 |
| [FTM](https://github.com/brianleect/etherscan-labels/tree/main/data/ftmscan) | [https://ftmscan.com](https://ftmscan.com) | [1085](https://github.com/brianleect/etherscan-labels/tree/main/./data/ftmscan/combined/combinedAllLabels.json) | ✅ ok | 26/3/2023 |
| [AVAX](https://github.com/brianleect/etherscan-labels/tree/main/data/avalanche) | [https://snowtrace.io](https://snowtrace.io) | [1062](https://github.com/brianleect/etherscan-labels/tree/main/./data/avalanche/combined/combinedAllLabels.json) | ✅ ok | 26/3/2023 |

Total Chains: 7

Total Labels: 42605

## Setup
1. On the command-line, run the command `pip install -r requirements.txt` while located at folder with code.
1. (Optional) Add ETHERSCAN_USER and ETHERSCAN_PASS to `sample.config.json` and rename to `config.json`
1. Run the script with the command `python main.py`.
1. Proceed to enter either `eth`, `bsc` or `poly` to specify chain of interest
1. Login to your ___scan account (Prevents popup/missing data)
1. Press enter in CLI once logged in
1. Proceed to enter either `single` (Retrieve specific label) or `all` (Retrieve ALL labels)
1. If `single`: Follow up with the specific label e.g. `exchange` , `bridge` ....
1. If `all`: Simply let it run (Take about ~1h+ to retrieve all, note that it occassionally crashes as well)
1. Individual JSON and CSV data is dumped into `data` subfolder. 
1. Consolidated JSON label info is dumped into `combined` subfolder.
