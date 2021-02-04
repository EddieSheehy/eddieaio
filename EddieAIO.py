from smyths.smythsold import smyths
import threading
import colorama
from colorama import Fore, Back, Style
import pandas as pd
import misc.miscfile

colorama.init()
df = pd.read_csv('profiles.csv', dtype=str)
file = open("profiles.csv")
numline = len(file.readlines())
numline = numline-2
print (numline)


print(Fore.CYAN)
print(r'''

$$$$$$$$\ $$$$$$$\  $$$$$$$\  $$$$$$\ $$$$$$$$\ 
$$  _____|$$  __$$\ $$  __$$\ \_$$  _|$$  _____|
$$ |      $$ |  $$ |$$ |  $$ |  $$ |  $$ |      
$$$$$\    $$ |  $$ |$$ |  $$ |  $$ |  $$$$$\    
$$  __|   $$ |  $$ |$$ |  $$ |  $$ |  $$  __|   
$$ |      $$ |  $$ |$$ |  $$ |  $$ |  $$ |                              
$$$$$$$$\ $$$$$$$  |$$$$$$$  |$$$$$$\ $$$$$$$$\ 
\________|\_______/ \_______/ \______|\________|  ''') 
print(Style.RESET_ALL) 
print(r'''                          
                                      ______   ______   ______  
                                    /      \ /      | /      \ 
                                    /$$$$$$  |$$$$$$/ /$$$$$$  |
                                    $$ |__$$ |  $$ |  $$ |  $$ |
                                    $$    $$ |  $$ |  $$ |  $$ |
                                    $$$$$$$$ |  $$ |  $$ |  $$ |
                                    $$ |  $$ | _$$ |_ $$ \__$$ |
                                    $$ |  $$ |/ $$   |$$    $$/ 
                                    $$/   $$/ $$$$$$/  $$$$$$/        
''')

threads = []


print('CHOOSE A SITE:\n\n')

def main():
    print('1. Smyths IE\n\n')
    choice = input('Run:')
    i=1
    if choice == '1':
      misc.miscfile.initprofile()
      for i in range(numline):
        i=i+1
        thread = threading.Thread(target=smyths.test)                 
        threads.append(thread)
      for thread in threads:
        #print(misc.miscfile.profile, '1st')
        misc.miscfile.profile= misc.miscfile.profile + 1
        thread.start()

      
              #for loop w/ append thread, run the loop for every row in profiles.csv


main()


#TOMORROW ADD IF FAIL TO CART RETRY - DONE
#MONITOR MODE - DONE
#PROFILE SUPPORT
#PROXY SUPPORT1
#2 OTHER SITES
#AUTH SYSTEM
#BASIC UI
