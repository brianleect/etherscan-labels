from selenium import webdriver
driver = webdriver.Chrome()
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
