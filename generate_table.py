import os
import json


def main():
    total_chains = 0
    total_labels = 0

    # Get the path of the current script
    current_path = os.path.dirname(os.path.abspath(__file__))

    # Print the current path
    print("Current path:", current_path)

    base_repo_url = "https://github.com/brianleect/etherscan-labels/tree/main"

    # Scan site mapping from chain to __scan url
    chain_map = {'eth': {'baseUrl': 'https://etherscan.io', 'savePath': './data/etherscan/combined/combinedAllLabels.json'},
                 'bsc': {'baseUrl': 'https://bscscan.com', 'savePath': './data/bscscan/combined/combinedAllLabels.json'},
                 'poly': {'baseUrl': 'https://polygonscan.com', 'savePath': './data/polygonscan/combined/combinedAllLabels.json'},
                 'opt': {'baseUrl': 'https://optimistic.etherscan.io', 'savePath': './data/optimism/combined/combinedAllLabels.json'},
                 'arb': {'baseUrl': 'https://arbiscan.io', 'savePath': './data/arbiscan/combined/combinedAllLabels.json'},
                 'ftm': {'baseUrl': 'https://ftmscan.com', 'savePath': './data/ftmscan/combined/combinedAllLabels.json'},
                 'avax': {'baseUrl': 'https://snowtrace.io', 'savePath': './data/avalanche/combined/combinedAllLabels.json'},
                 }
    table_header = "| Chain | Site | Label Count |"
    table_separator = "|-------|------|-------------|"
    table_rows = []

    for chain, chain_data in chain_map.items():
        base_url = chain_data['baseUrl']
        chainDataLink = base_repo_url + chain_data['savePath'][1:-
                                                               len('/combined/combinedAllLabels.json')]
        print(chainDataLink)

        try:
            with open(chain_map[chain]['savePath'], 'r', encoding='utf-8') as f:
                combined_data = json.load(f)
                label_count = len(combined_data)
                print('label:', label_count)
                total_labels += label_count
        except Exception as e:
            print(f"Error reading file {chain_map[chain]['savePath']}: {e}")
            label_count = 0

        row = f"| [{chain.upper()}]({chainDataLink}) | [{base_url}]({base_url}) | [{label_count}]({base_repo_url}/{chain_data['savePath']}) |"
        table_rows.append(row)

    table = "\n".join([table_header, table_separator] + table_rows)
    print(table)
    print(f"Total Chains: {len(chain_map)}")
    print(f"Total Labels: {total_labels}")


if __name__ == "__main__":
    main()
