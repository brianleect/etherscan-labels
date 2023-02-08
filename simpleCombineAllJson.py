
import json
import os.path

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


combineAllJson()
