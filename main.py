import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
import json
from time import sleep, time



url = "https://gh.....to........ir"  #We don't want to clear the real url
def run_browser(headless = True):
    options = webdriver.ChromeOptions()
    if headless == True:
        options.add_argument('--headless')
    driver = webdriver.Chrome(options=options)
    return driver

def get_products_link(driver):
    links_set = set()
    for i in range(1,3):
        driver.get(f"{url}/shop/page/{i}?per_page=500")
        tag_A_s = driver.find_element(By.CSS_SELECTOR,"body > div.website-wrapper > div.main-page-wrapper > div > div > div").find_elements(By.CSS_SELECTOR,"a")
        for a in tag_A_s:
            link = a.get_attribute("href")
            if link.startswith(f"{url}/product/"):
                links_set.add(link)
    links = list(links_set)
    return links

# links = get_products_link()


def login(driver):
    driver.get(f"{url}/my-account/")
    driver.find_element(By.CSS_SELECTOR,"#username").send_keys("username123")
    driver.find_element(By.CSS_SELECTOR,"#password").send_keys("password123")
    driver.find_element(By.CSS_SELECTOR,"#post-10 > div > div > div.wd-registration-page.wd-no-registration > form > p:nth-child(3) > button").click()
    sleep(7)


def get_detail_product(driver):
    name = None
    status = None
    discount = None
    real_price = None
    models = None
    colors = None
    image_url = None

    name = driver.find_element(By.XPATH,
                               "/html/body/div[1]/div[1]/div/div/div/div[2]/div[1]/div[2]/div/div/div[2]/div/h1").text

    discount = "0"
    try:
        status = driver.find_element(By.XPATH,
                                     "/html/body/div[1]/div[1]/div/div/div/div[2]/div[1]/div[2]/div/div/div[1]/div/div/div[1]/div/span").text
        if status == "اتمام موجودی":
            status = False
        else:
            discount = status.replace("%", "").replace("-", "")
            status = True
    except:
        status = True


    if discount == "0":
        real_price = driver.find_element(By.XPATH,
                                         "/html/body/div[1]/div[1]/div/div/div/div[2]/div[1]/div[2]/div/div/div[2]/div/p/span/bdi").text.replace(
            " تومان", "")


    else:
        real_price = driver.find_element(By.XPATH,
                                         "/html/body/div[1]/div[1]/div/div/div/div[2]/div[1]/div[2]/div/div/div[2]/div/p/del/span/bdi").text.replace(
            " تومان", "")


    models = driver.find_elements(By.XPATH,
                                  "/html/body/div[1]/div[1]/div/div/div/div[2]/div[1]/div[2]/div/div/div[2]/div/form/div/table/tbody/tr[2]/td/ul/li")

    colors = driver.find_elements(By.XPATH,
                                  "/html/body/div[1]/div[1]/div/div/div/div[2]/div[1]/div[2]/div/div/div[2]/div/form/div/table/tbody/tr[1]/td/ul/li")



    while True:
        try:
            image_url = driver.find_element(By.XPATH,
                                            "/html/body/div[1]/div[1]/div/div/div/div[2]/div[1]/div[2]/div/div/div[1]/div/div/div[1]/figure/div[1]/div/div[1]/div/figure/img").get_attribute(
                "src")
            break
        except:
            try:
                image_url = driver.find_element(By.XPATH,
                                                "/html/body/div[1]/div[1]/div/div/div/div[2]/div[1]/div[2]/div/div/div[1]/div/div/div[1]/figure/div[1]/div/div/div/figure/a/img").get_attribute(
                    "src")
                break
            except:
                pass

    colors_list = []
    for c in colors:
        if c.get_attribute("tabindex") == "0":
            colors_list.append({"color": c.get_attribute("title"), "status": True})
        elif c.get_attribute("tabindex") == "-1":
            colors_list.append({"color": c.get_attribute("title"), "status": False})

    models_list = []
    for m in models:
        if m.get_attribute("tabindex") == "0":
            models_list.append({"device": m.text, "status": True})
        elif m.get_attribute("tabindex") == "-1":
            models_list.append({"device": m.text, "status": False})

    return {"name": name, "status": status, "real_price": real_price, "discount": discount, "color": colors_list,
            "device": models_list, "image_url": image_url}





def main(headless = True, waiting_time= 300):
    driver = run_browser(headless=headless)
    links = get_products_link(driver)
    login(driver)

    data = dict()
    while True:
        for i in range(len(links)):
            # print(f"{i/len(links)} %")
            driver.get(links[i])
            try:
                data[links[i]] = get_detail_product(driver)
            except:
                print("passed url is"+links[i])
        else:
            #saving data as excel file
            pd.DataFrame(data).T.to_excel("torando_data.xlsx")


            #saving as json
            with open("tornado_data.json", "w") as outfile:
                json.dump(data, outfile)
        sleep(waiting_time)
        links = get_detail_product(driver)


if __name__ == "__main__":
    gui_br = input("Do you need GUI browser? [y/n]: ")
    if gui_br == 'y':
        headless = False
    elif gui_br == 'n':
        headless = True
    else:
        print("not acceptable response")
        quit()


    waiting_time = int(input("How many seconds the program should wait between two tries? [ex. 300]: "))

    main(headless=headless,waiting_time=waiting_time)