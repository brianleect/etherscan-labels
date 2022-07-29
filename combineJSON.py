import json
import os

combinedJSON = {}

# iterating over all files
for files in os.listdir('./data'):
    if files.endswith('json'):
        print(files)  # printing file name of desired extension
        with open('./data/{}'.format(files)) as f:
            dictData = json.load(f)
            for address, nameTag in dictData.items():
                if address not in combinedJSON:
                    combinedJSON[address] = []
                combinedJSON[address].append(
                    nameTag+' ({})'.format(files[:-5]))
    else:
        continue

with open('combinedJSON.json', 'w', encoding='utf-8') as f:
    json.dump(combinedJSON, f, ensure_ascii=True)
