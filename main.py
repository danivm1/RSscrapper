from selenium import webdriver
from selenium.webdriver.support.wait import WebDriverWait as wdw
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException, TimeoutException

import pandas as pd

import re

options = webdriver.ChromeOptions()
options.add_argument("--headless=new")

driver = webdriver.Chrome(options)

wait = wdw(driver, 10)


cols = ["Nome"
       ,"Etiquetas"
       ,"Endereço"
       ,"Telefone"
       ,"Descrição"
       ,"Palavras-Chave"]

df = pd.DataFrame(columns=cols)


page = 0

while 1:
    page += 1
    print(page)
    driver.get(f"https://app.ajuders.com.br/?page={page}")
    
    try:
        mainElem = wait.until(ec.visibility_of_element_located((By.ID, "rgitems")))
    except (TimeoutException, NoSuchElementException):
        break

    
    while 1:
        lastElemIndex = len(mainElem.find_elements(By.CSS_SELECTOR, ":scope > div"))
        lastElem = wait.until(ec.visibility_of(mainElem.find_element(By.CSS_SELECTOR, f":scope > div:nth-child({lastElemIndex})")))

        driver.execute_script("arguments[0].scrollIntoView();", lastElem)

        try:
            wdw(driver, 3).until(ec.visibility_of(mainElem.find_element(By.CSS_SELECTOR, f":scope > div:nth-child({lastElemIndex+1})")))
        except NoSuchElementException:
            break


    lastElemIndex = len(mainElem.find_elements(By.CSS_SELECTOR, ":scope > div"))

    for i in range(1, lastElemIndex+1):
        print(f"{page} -> {i}")
        generalDataQuery = f":scope > div:nth-child({i}) > div > div > div:nth-child(2) > div > div"
        nameQuery = f":scope > div > div > div > div"
        tagListQuery = f":scope > div:nth-child(2) > div"
        addressQuery = f":scope > div:nth-child(3) > div > div:nth-child(2) > div"
        phoneQuery = f":scope > div:nth-child(3) > div:nth-child(2) > div:nth-child(2) > div"
        descriptionQuery = f":scope > div:nth-child(4) > div"
        keywordListQuery = f":scope > div:nth-child(5) > div > div"
        keywordNameQuery = f":scope > div > div > div"

        infoElem = mainElem.find_element(By.CSS_SELECTOR, generalDataQuery)

        name = infoElem.find_element(By.CSS_SELECTOR, nameQuery).text
        address = infoElem.find_element(By.CSS_SELECTOR, addressQuery).text
        try: phone = infoElem.find_element(By.CSS_SELECTOR, phoneQuery).text
        except: phone = ""

        rgxDesc = re.compile("\n+")
        description = rgxDesc.sub("; ", infoElem.find_element(By.CSS_SELECTOR, descriptionQuery).text)

        rgxTags = re.compile("\n.*")

        tagList = infoElem.find_elements(By.CSS_SELECTOR, tagListQuery)
        tags = ";".join(rgxTags.sub("", tag.text) for tag in tagList)

        keywordList = infoElem.find_elements(By.CSS_SELECTOR, keywordListQuery)
        keywords = ";".join(keyword.find_element(By.CSS_SELECTOR, keywordNameQuery).text for keyword in keywordList)

        df.loc[len(df.index)] = [name, tags, address, phone, description, keywords]
    

df.to_csv("./data.csv", sep="|", index=False)
df.to_json("./data.json", orient="records")
df.to_xml("./data.xml")
df.to_markdown("./data.md")