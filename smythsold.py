from discord_webhook import *
from threading import Thread
import requests
import time
from xpath import *
from bs4 import BeautifulSoup as bs
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import csv
import pandas as pd
import colorama
from colorama import Fore, Back, Style
import json
import misc.miscfile

colorama.init()

options = Options()
options.add_argument("--silent")
options.add_argument("--log-level=3")
options.add_argument("--headless")
options.add_argument("--window-size=%s" % '1920,1080')
options.add_experimental_option('excludeSwitches', ['enable-logging'])
options.binary_location = 'C:\Program Files (x86)\Google\Chrome Beta\Application\chrome.exe'

headers = {'User-Agent': 'Mozilla/5.0 (Windows NT x.y; rv:10.0) Gecko/20100101 Firefox/10.0'}


s = requests.Session() # cookies are stored in the session

qty = 1

class smyths:

    def test(): 
        print(misc.miscfile.profile)
        #print('hi')
        df = pd.read_csv('profiles.csv', dtype=str)
        email = df.email[0]
        email2 = df.email[1]
        print(email)
        print(email2)
        time.sleep(10)

    def start():
        global url
        url = 'https://www.smythstoys.com/ie/en-ie/outdoor/bikes/balance-bikes/12-inch-peppa-pig-balance-bike/p/163971'
        content = s.get(url,headers=headers)
        soup = bs(content.text, 'lxml')
        global csrf_token
        csrf_token = soup.find("input", {'name':'CSRFToken'}).get('value')
        global basketcheck
        basketcheck = soup.find("a", {'href':'/ie/en-ie/cart'}).span
        global productcode
        productcode = soup.find("div", {'id':'bv-container'}).get('data-bv-productid')
        global producttitle
        producttitle = soup.find("h1", {'class':'margn_top_10'}).text
        global productphoto
        productphoto = soup.find("img", {'class':'responsive-image'}).get('src')
        global productprice
        productprice = soup.find("div", {'class':'price_tag'}).span.text
        global preordercheck
        preordercheck = str(soup.find("form", {"id": "customAddToCartForm"}).find('button'))
        smyths.checkinstock()


    def checkinstock():
        content = s.get(url,headers=headers)
        if not content is None:
            soup = bs(content.text, 'lxml')
            stockSmythsDisk = str(soup.find("form", {"id": "customAddToCartForm"}).find('button'))
        if stockSmythsDisk[53:66] == 'js-enable-btn':
            smyths.addtocart()
        else:
            smyths.monitor()

    def monitor():
            print('[MONITOR] - '+url)
            time.sleep(5)
            smyths.checkinstock()
        
    def addtocart():
        #The post adds the item to cart.
        info = s.get(url, headers=headers)
        soup = bs(info.text, 'lxml')
        atcpayload = {'CSRFToken':csrf_token,'productCodePost': productcode, 'qty': qty}
        preorderatcpayload = {'CSRFToken':csrf_token,'productCodePost': productcode, 'qty': qty, 'preOrder':'true'}
        #print(csrf_token,productcode,url)
        if 'Pre-Order' in preordercheck:
            post = s.post("https://www.smythstoys.com/ie/en-ie/cart/add", data=preorderatcpayload,  headers=headers)
        else:
            post = s.post("https://www.smythstoys.com/ie/en-ie/cart/add", data=atcpayload,  headers=headers)
        get = s.get("https://www.smythstoys.com/ie/en-ie/login/checkout", headers=headers)
        soup = bs(get.text, 'lxml')
        basketcheck2 = soup.find("a", {'href':'/ie/en-ie/cart'}).span

        if basketcheck2.text != '0':
            print(Fore.CYAN+'\n\n[STATUS] - Sucessfully Added To Cart - Quantity:',qty,'(1/5)'+Style.RESET_ALL)

            smyths.guestcheckout()
            #print('AMOUNT OF ITEMS IN CART', basketcheck2.text)   
            #print('Open Cart',get.status_code)
                
            #print('AMOUNT OF ITEMS IN CART', basketcheck2.text)   
            #print(csrf_token)
            
        else:

            print('[ERROR] - Error Adding To Cart Retrying...')
            time.sleep(2)

            smyths.start()
            

    def guestcheckout():
        df = pd.read_csv('profiles.csv', dtype=str)
        email = df.email[profile]
        
        guestcheckpayload = {'CSRFToken':csrf_token, 'email':email, 'confirmEmail':email}
        post = s.post('https://www.smythstoys.com/ie/en-ie/login/checkout/guest', data=guestcheckpayload, headers=headers)
        #print('Guest Checkout start',post.status_code)
        #print('AMOUNT OF ITEMS IN CART', basketcheck2.text)
        #print('before add delivery',post.text) 
        print(Fore.YELLOW+'[STATUS] - Sucessfully Initiated Guest Checkout (2/5)'+Style.RESET_ALL)
        smyths.deliverystep()

    def deliverystep():
        df = pd.read_csv('profiles.csv', dtype=str)
        email = df.email[profile]
        city = df.city[profile]
        fname = df.firstname[profile]
        lname = df.lastname[profile]
        phone = df.phone[profile]
        line1 = df.addressline1[profile]
        line2 = df.addressline2[profile]
        isocode = df.isocode[profile]
        postcode = df.postcode[profile]
        county = df.county[profile]

        deliveryaddresspayload = {
            'CSRFToken':csrf_token,
            'address.firstName':fname,
            'address.lastName':lname,
            'address.phone':phone,
            'address.line1':line1,
            'address.line2':line2,
            'address.townCity':city,
            'address.county':county,
            'address.postcode':postcode,
            'address.countryIso':isocode,
            'address.saveInAddressBook':'false',
            'deviceType':'Desktop',
            'deliveryChannel':'HOME_DELIVERY',
            'customerType':'Guest'
            }

        shippingconfirmpayload= {'delivery_method':'STANDARD_REGULAR', 'CSRFToken':csrf_token, 'deviceType':'Desktop'}
            
        post = s.post('https://www.smythstoys.com/ie/en-ie/checkout/multi/delivery-address/add',data=deliveryaddresspayload, headers=headers)
        #print('Address Added',post.status_code)
        get = s.get('https://www.smythstoys.com/ie/en-ie/checkout/multi/delivery-method/choose', headers=headers)
        post = s.post('https://www.smythstoys.com/ie/en-ie/checkout/multi/delivery-method/select',data=shippingconfirmpayload, headers=headers)
        #print('Shipping Confirmed',post.status_code)
        print(Fore.YELLOW+'[STATUS] - Successfully Submitted Address (3/5)'+Style.RESET_ALL)
        smyths.payment()


    def payment():
        df = pd.read_csv('profiles.csv', dtype=str)
        card = df.cardnumber[profile]
        card1 = card[0:4]
        card2 = card[4:8]
        card3 = card[8:12]
        card4 = card[12:16]
        expmonth = df.expmonth[profile]
        expyear = df.expyear[profile]
        cvv = df.cvv[profile]

        if expmonth == '01': expmonthxpath = '/html/body/div[7]/section/div/div/div[2]/div/div/div/div/div[1]/div[1]/div[2]/div[2]/div[2]/div[2]/div[3]/div[2]/div/div[1]/div[1]/div/div/ul/li[2]/a'

        if expmonth == '02': expmonthxpath = '/html/body/div[7]/section/div/div/div[2]/div/div/div/div/div[1]/div[1]/div[2]/div[2]/div[2]/div[2]/div[3]/div[2]/div/div[1]/div[1]/div/div/ul/li[3]/a'

        if expmonth == '03': expmonthxpath = '/html/body/div[7]/section/div/div/div[2]/div/div/div/div/div[1]/div[1]/div[2]/div[2]/div[2]/div[2]/div[3]/div[2]/div/div[1]/div[1]/div/div/ul/li[4]/a'

        if expmonth == '04': expmonthxpath = '/html/body/div[7]/section/div/div/div[2]/div/div/div/div/div[1]/div[1]/div[2]/div[2]/div[2]/div[2]/div[3]/div[2]/div/div[1]/div[1]/div/div/ul/li[5]/a'

        if expmonth == '05': expmonthxpath = '/html/body/div[7]/section/div/div/div[2]/div/div/div/div/div[1]/div[1]/div[2]/div[2]/div[2]/div[2]/div[3]/div[2]/div/div[1]/div[1]/div/div/ul/li[6]/a'

        if expmonth == '06': expmonthxpath = '/html/body/div[7]/section/div/div/div[2]/div/div/div/div/div[1]/div[1]/div[2]/div[2]/div[2]/div[2]/div[3]/div[2]/div/div[1]/div[1]/div/div/ul/li[7]/a'

        if expmonth == '07': expmonthxpath = '/html/body/div[7]/section/div/div/div[2]/div/div/div/div/div[1]/div[1]/div[2]/div[2]/div[2]/div[2]/div[3]/div[2]/div/div[1]/div[1]/div/div/ul/li[8]/a'

        if expmonth == '08': expmonthxpath = '/html/body/div[7]/section/div/div/div[2]/div/div/div/div/div[1]/div[1]/div[2]/div[2]/div[2]/div[2]/div[3]/div[2]/div/div[1]/div[1]/div/div/ul/li[9]/a'

        if expmonth == '09': expmonthxpath = '/html/body/div[7]/section/div/div/div[2]/div/div/div/div/div[1]/div[1]/div[2]/div[2]/div[2]/div[2]/div[3]/div[2]/div/div[1]/div[1]/div/div/ul/li[10]/a'

        if expmonth == '10': expmonthxpath = '/html/body/div[7]/section/div/div/div[2]/div/div/div/div/div[1]/div[1]/div[2]/div[2]/div[2]/div[2]/div[3]/div[2]/div/div[1]/div[1]/div/div/ul/li[11]/a'

        if expmonth == '11': expmonthxpath = '/html/body/div[7]/section/div/div/div[2]/div/div/div/div/div[1]/div[1]/div[2]/div[2]/div[2]/div[2]/div[3]/div[2]/div/div[1]/div[1]/div/div/ul/li[12]/a'

        if expmonth == '12': expmonthxpath = '/html/body/div[7]/section/div/div/div[2]/div/div/div/div/div[1]/div[1]/div[2]/div[2]/div[2]/div[2]/div[3]/div[2]/div/div[1]/div[1]/div/div/ul/li[13]/a'

        if expyear == '21': expyearxpath = '/html/body/div[7]/section/div/div/div[2]/div/div/div/div/div[1]/div[1]/div[2]/div[2]/div[2]/div[2]/div[3]/div[2]/div/div[1]/div[2]/div/div/ul/li[2]/a'

        if expyear == '22': expyearxpath = '/html/body/div[7]/section/div/div/div[2]/div/div/div/div/div[1]/div[1]/div[2]/div[2]/div[2]/div[2]/div[3]/div[2]/div/div[1]/div[2]/div/div/ul/li[3]/a'

        if expyear == '23': expyearxpath = '/html/body/div[7]/section/div/div/div[2]/div/div/div/div/div[1]/div[1]/div[2]/div[2]/div[2]/div[2]/div[3]/div[2]/div/div[1]/div[2]/div/div/ul/li[4]/a'

        if expyear == '24': expyearxpath = '/html/body/div[7]/section/div/div/div[2]/div/div/div/div/div[1]/div[1]/div[2]/div[2]/div[2]/div[2]/div[3]/div[2]/div/div[1]/div[2]/div/div/ul/li[5]/a'

        if expyear == '25': expyearxpath = '/html/body/div[7]/section/div/div/div[2]/div/div/div/div/div[1]/div[1]/div[2]/div[2]/div[2]/div[2]/div[3]/div[2]/div/div[1]/div[2]/div/div/ul/li[6]/a'

        if expyear == '26': expyearxpath = '/html/body/div[7]/section/div/div/div[2]/div/div/div/div/div[1]/div[1]/div[2]/div[2]/div[2]/div[2]/div[3]/div[2]/div/div[1]/div[2]/div/div/ul/li[7]/a'

        if expyear == '27': expyearxpath = '/html/body/div[7]/section/div/div/div[2]/div/div/div/div/div[1]/div[1]/div[2]/div[2]/div[2]/div[2]/div[3]/div[2]/div/div[1]/div[2]/div/div/ul/li[8]/a'

        if expyear == '28': expyearxpath = '/html/body/div[7]/section/div/div/div[2]/div/div/div/div/div[1]/div[1]/div[2]/div[2]/div[2]/div[2]/div[3]/div[2]/div/div[1]/div[2]/div/div/ul/li[9]/a'

        if expyear == '29': expyearxpath = '/html/body/div[7]/section/div/div/div[2]/div/div/div/div/div[1]/div[1]/div[2]/div[2]/div[2]/div[2]/div[3]/div[2]/div/div[1]/div[2]/div/div/ul/li[10]/a'

        if expyear == '30': expyearxpath = '/html/body/div[7]/section/div/div/div[2]/div/div/div/div/div[1]/div[1]/div[2]/div[2]/div[2]/div[2]/div[3]/div[2]/div/div[1]/div[2]/div/div/ul/li[11]/a'

        if expyear == '31': expyearxpath = '/html/body/div[7]/section/div/div/div[2]/div/div/div/div/div[1]/div[1]/div[2]/div[2]/div[2]/div[2]/div[3]/div[2]/div/div[1]/div[2]/div/div/ul/li[12]/a'
        
        driver = webdriver.Chrome(executable_path='./chromedriver',options=options)
        driver.get('https://www.smythstoys.com/ie/en-ie/')
        print(Fore.CYAN+'[STATUS] - Adding Cookies'+Style.RESET_ALL)
        for c in s.cookies :
            driver.add_cookie({'name': c.name, 'value': c.value, 'path': c.path, 'expires / max-age': c.expires})
            
        print(Fore.YELLOW+'[STATUS] - Initiating Checkout (4/5)'+Style.RESET_ALL)
        driver.get('https://www.smythstoys.com/ie/en-ie/checkout/multi/payment-method/add?siteName=IE+Site&isCirculatorScriptEnable=true&pageTitle=Checkout+Delivery+Options')
        time.sleep(2)
        WebDriverWait(driver,0.1).until(EC.element_to_be_clickable((By.XPATH,'/html/body/div[4]/div/div/div[1]/div[4]/div[1]/button'))).click()
        time.sleep(0.2)
        cardpt1 = driver.find_element_by_xpath('//*[@id="cardNumberPart1"]')
        cardpt1.send_keys(card1)
        cardpt2 = driver.find_element_by_xpath('//*[@id="cardNumberPart2"]')
        cardpt2.send_keys(card2)
        cardpt3 = driver.find_element_by_xpath('//*[@id="cardNumberPart3"]')
        cardpt3.send_keys(card3)
        cardpt4 = driver.find_element_by_xpath('//*[@id="cardNumberPart4"]')
        cardpt4.send_keys(card4)
        expmonth = driver.find_element_by_xpath('/html/body/div[7]/section/div/div/div[2]/div/div/div/div/div[1]/div[1]/div[2]/div[2]/div[2]/div[2]/div[3]/div[2]/div/div[1]/div[1]/div/button')
        expmonth.click()
        expmonthselector = driver.find_element_by_xpath(expmonthxpath)
        expmonthselector.click()
        expyear = driver.find_element_by_xpath('/html/body/div[7]/section/div/div/div[2]/div/div/div/div/div[1]/div[1]/div[2]/div[2]/div[2]/div[2]/div[3]/div[2]/div/div[1]/div[2]/div/button')
        expyear.click()
        expyearselector = driver.find_element_by_xpath(expyearxpath)
        expyearselector.click()
        cvvinfo = driver.find_element_by_xpath('//*[@id="cardCvn"]')
        cvvinfo.send_keys(cvv)
        tncconfirm = driver.find_element_by_xpath('/html/body/div[7]/section/div/div/div[2]/div/div/div/div/div[1]/div[3]/div/div/label[1]/div')
        tncconfirm.click()
        placeorderbtn = driver.find_element_by_xpath('//*[@id="placeOrder"]')
        placeorderbtn.click()
        print(Fore.YELLOW+'[STATUS] - Submitting Order [5/5]'+Style.RESET_ALL)
        time.sleep(5.5)
        while 'cybersource' in driver.current_url:
            if driver.current_url == 'https://secureacceptance.cybersource.com/silent/payer_authentication/hybrid?ccaAction=load':
                print(Fore.BLUE+'[ALERT] 3DS AUTHENTICATION DETECTED'+Style.DIM)
                time.sleep(10)     

        if 'orderConfirmation' in driver.current_url:
            with open('config.json') as f:
                config_json = json.loads(f.read())
            print(Fore.GREEN+'[SUCCESS] - SUCCESSFUL CHECKOUT'+Style.RESET_ALL)
            webhook_url = config_json['webhook_url']
            user = config_json['discord_id']
            webhook = DiscordWebhook(url=webhook_url, username="EddieAIO", avatar_url='https://images.fineartamerica.com/images/artworkimages/mediumlarge/3/capitalism-jack-andriano.jpg')
            embed = DiscordEmbed(title='Successful Checkout', color=7419530)
            embed.add_embed_field(name='Store', value='Smyths IE', inline=False)
            embed.add_embed_field(name='Product', value=producttitle, inline=False)
            embed.add_embed_field(name='Price', value=productprice, inline=False)
            embed.add_embed_field(name='User', value=user, inline=False)
            embed.add_embed_field(name='Order Confirmed', value=driver.current_url, inline=False)
            embed.set_thumbnail(url=productphoto)
            embed.set_footer(text='EddieAIO',icon_url='https://images.fineartamerica.com/images/artworkimages/mediumlarge/3/capitalism-jack-andriano.jpg')
            embed.set_timestamp()
            webhook.add_embed(embed)
            webhook.execute()
            
        else:
            print(Fore.RED+'[ERROR] - FAILED CHECKOUT'+Style.RESET_ALL)
            time.sleep(2)
            smyths.guestcheckout()

    
