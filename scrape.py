import pandas as pd
from selenium import webdriver
from selenium.webdriver.edge.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
import time
import os


class ExtractData:
    
    def __init__(self, primary_option):
        
        self.primary_option = primary_option
        self.service = Service(executable_path='/Users/dhruvparikh/Desktop/Webscrape/edgedriver_mac64_m1/msedgedriver')
        self.driver = webdriver.Edge(service=self.service)
        
    
    def make_link(self, link, year_selected):
        
        first_part = '/'.join(link.split('/')[:6])
        league_name = '-'.join(link.split('/')[-1].split('-')[:-1])
        final_link = f'{first_part}/{year_selected}/{year_selected}-{league_name}-Stats'
        
        return(final_link)
    
    
    def go_to(self,link):
        
        print(f'moved to {link} \n')
        time.sleep(2)
        
        self.driver.get(link)
    
    
    def extract_name(self,link):
        
        value = link.split('/#')
        
        if len(value)>1:
            return(value[1])
        
        else:
            return None
        
        
    def make_dict(self, option_list):
        
        dictionary = {}
        
        text = [ a_tag.text for a_tag in option_list]
        links = [ a_tag.get_attribute('href') for a_tag in option_list]
        
        for i,j in zip(text,links):
            dictionary[i] = j
            
        return(dictionary)
    
    
    def input_text(self, dictionary, req_range = 0):
        
        to_print = {}
        
        if req_range!=0:
            
            for i in range(req_range):
                for j,k in enumerate(dictionary.keys()):
                    to_print[j+1] = k
                    
        else:
            
            for j,k in enumerate(dictionary.keys()):
                to_print[j+1] = k
                
        return(to_print)
    
    
    def take_input(self, value):
        
        text_dict = self.input_text(value)
        
        for i,j in text_dict.items():
            print(f'{i}.  {j}')
            
        option = int(input('Enter league option :-\t'))
        
        return(text_dict[option])
    
    
    def start(self, by, value, state):
    
        link_dict = self.make_dict(
                state.find_elements(by, value))
        
        selected = self.take_input(link_dict)
        name = self.extract_name(link_dict[selected])
        
        if name == None:
            name = selected
        
        return(name, link_dict[selected])
        
        
    def final_func(self):
        
        name_list = ['gca', 'passing_types', 'defense', 'possession', 'passing',
                     'shooting', 'misc', 'keepers']
        
        name_dict = {}
        for i in name_list:
            name_dict[i] = 1
            
        text_dict = self.input_text(name_dict)
        
        for i,j in text_dict.items():
            print(f'{i}.  {j}')
            
        selected = list(input('Enter List of selection :- \t'))
        
        needed_data = []
        for i in selected:
            needed_data.append(text_dict.get(int(i)))
        
        return(needed_data)
        
        
    def scrape_tables(self, name):
        
        table_data = []
        
        table_div = self.driver.find_element(By.ID,f'div_stats_{name}')
        table = table_div.find_element(By.TAG_NAME,'table')
        
        table_header = table.find_element(By.TAG_NAME,'thead')
        header = table_header.find_elements(By.TAG_NAME,'tr')[1:2]
        for i in header:
            th = i.find_elements(By.TAG_NAME,'th')
            header_data = [ head.text for head in th]
        
        table_rows = table.find_elements(By.TAG_NAME,'tr')
        
        for row in table_rows:
            
            cells = row.find_elements(By.TAG_NAME,'td')
            row_data = [ cell.text for cell in cells ]
            table_data.append(row_data)
            
        df = pd.DataFrame(data=table_data, columns = header_data[1:])
        
        return(df)
        
        
    def scrape(self):
        
        self.driver.get('https://fbref.com/en/comps/')
        self.driver.minimize_window()
        option_list = self.driver.find_element(By.ID,'inpage_nav')
        
        time.sleep(3)
        
        first_filter, first_link = self.start(by = By.TAG_NAME, 
                                              value = 'a', state = option_list)
        
        self.go_to(first_link)
        
        div_class = self.driver.find_element(By.ID,first_filter)
        state_2 = div_class.find_element(By.TAG_NAME,'table')
  
        second_filter, second_link = self.start(by= By.CSS_SELECTOR, 
                   value = 'th.left[data-stat="league_name"] a',
                   state = state_2)
        
        
        self.go_to(second_link)
        
        year_dict = {}
        for i in range(2015,2025):
            year_dict[str(i)+'-'+str(i+1)] = 1
            
        selected_year = self.take_input(year_dict)
        
        self.go_to(self.make_link(second_link, selected_year))
        
        goto_links = self.final_func()
        
        dataframe_dictionary = {}
        for i in goto_links:
            first_part = '/'.join(second_link.split('/')[:6])
            league_name = '-'.join(second_link.split('/')[-1].split('-')[:-1])
            final_link = f'{first_part}/{i}/{league_name}'
            
            self.go_to(final_link)
            dataframe_dictionary[f'{league_name}_{i}'] = self.scrape_tables(i)
            time.sleep(5)
        
        time.sleep(2)
        self.driver.quit()
        return(dataframe_dictionary)
        
        
    def test(self):
        self.driver.get('https://fbref.com/en/comps/9/passing/Premier-League-Stats')
        time.sleep(3)
        
        dataframe = pd.DataFrame()
        
        div = self.driver.find_element(By.ID,'div_stats_passing')
        table = div.find_element(By.TAG_NAME,'table')
        count=0
        for i in table.find_elements(By.TAG_NAME,'tr'):
            count+=1
            for j in i.find_elements(By.TAG_NAME,'td'):
                print(j.text)
            if count>10:
                break
                
        
        
        self.driver.quit()