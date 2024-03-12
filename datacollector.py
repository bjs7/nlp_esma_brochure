import time
import requests
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import Select


url = 'https://registers.esma.europa.eu/publication/searchRegister?core=esma_registers_priii_documents'

driver = webdriver.Chrome()
driver.get(url)
driver.maximize_window()

driver.find_element(By.CSS_SELECTOR, '#searchSolrButton').click()


class SecurityType:

    def __init__(self, chrSearch = None, document_type = None, structure_type = None, home_member_state = None, host_member_states = None,
                 issuer_offeror_guarantor_information = None, applicable_annexes_disclosure_regimes = None, EU_growth_prospectus_category = None,
                 national_document_ID = None, ISIN = None, prospectus_type = None, prospectus_ID = None, last_update_date = None, approval_or_filing_date = None,
                 passported = None, criteria_add = None):

        self.chrSearch = chrSearch
        self.document_type = document_type
        self.structure_type = structure_type
        self.home_member_state = home_member_state
        self.host_member_states = host_member_states
        self.issuer_offeror_guarantor_information = issuer_offeror_guarantor_information
        self.applicable_annexes_disclosure_regimes = applicable_annexes_disclosure_regimes
        self.EU_growth_prospectus_category = EU_growth_prospectus_category
        self.national_document_ID = national_document_ID
        self.ISIN = ISIN
        self.prospectus_type = prospectus_type
        self.prospectus_ID = prospectus_ID
        self.last_update_date = last_update_date
        self.approval_or_filing_date = approval_or_filing_date
        self.passported = passported
        self.criteria_add = criteria_add

    def reset(self):
        driver.refresh()

    def dropdownselector(self, type, type_value):
        Select(driver.find_element(By.CSS_SELECTOR, f"select[name={type}]")).select_by_visible_text(
            type_value)

    def f_search(self):

        if self.chrSearch is not None:
            driver.find_element(By.ID, 'keywordField').clear()
            driver.find_element(By.ID, 'keywordField').send_keys(self.chrSearch)

        if self.document_type is not None:
            self.dropdownselector('document_type', self.document_type)

        if self.structure_type is not None:
            self.dropdownselector('structure_type_code', self.structure_type)

        if self.home_member_state is not None:
            self.dropdownselector('home_member_state_code', self.home_member_state)

        if self.host_member_states is not None:
            self.dropdownselector('pscn_country_code', self.host_member_states)

        if self.issuer_offeror_guarantor_information is not None:
            self.dropdownselector('party_type', self.issuer_offeror_guarantor_information)

        if self.applicable_annexes_disclosure_regimes is not None:
            self.dropdownselector('disclosure_regime', self.applicable_annexes_disclosure_regimes)

        if self.EU_growth_prospectus_category is not None:
            self.dropdownselector('eu_growth_prosp_cat_code', self.EU_growth_prospectus_category)

        if self.national_document_ID is not None:
            driver.find_element(By.NAME, 'national_document_id').clear()
            driver.find_element(By.NAME, 'national_document_id').send_keys(self.national_document_ID)

        if self.ISIN is not None:
            driver.find_element(By.NAME, 'isin_isin').clear()
            driver.find_element(By.NAME, 'isin_isin').send_keys(self.ISIN)

        if self.prospectus_type is not None:
            self.dropdownselector('prospectus_type_code', self.prospectus_type)

        if self.prospectus_ID is not None:
            driver.find_element(By.NAME, 'prospectus_id').clear()
            driver.find_element(By.NAME, 'prospectus_id').send_keys(self.prospectus_ID)

        if self.last_update_date is not None:
            driver.find_element(By.ID, 'dp1707843150374').send_keys(self.last_update_date[0])
            driver.find_element(By.ID, 'dp1707843150375').send_keys(self.last_update_date[1])

        if self.approval_or_filing_date is not None:
            driver.find_element(By.ID, 'dp1707843150378').send_keys(self.approval_or_filing_date[0])
            driver.find_element(By.ID, 'dp1707843150379').send_keys(self.approval_or_filing_date[1])

        if self.passported is not None:
            self.dropdownselector('is_passported', self.passported)

        if self.criteria_add is not None:
            Select(driver.find_element(By.CSS_SELECTOR, f"select[id=ID005]")).select_by_visible_text(
                self.criteria_add)

        driver.find_element(By.CSS_SELECTOR, '#searchSolrButton').click()

    def f_findrelevantcolumns(self, vCols='Physical Document'):
        vNamecolumns = driver.find_element(By.XPATH, '/html/body/div[2]/div[4]/div[2]/div/div[3]/div[3]/table/thead/tr').find_elements(By.TAG_NAME, 'th')
        iIndecies = [index for index, i in enumerate(vNamecolumns) if i.text == vCols].pop()
        return iIndecies

    def downloadcurrentpage(self):
        vSecurities = driver.find_element(By.XPATH, '/html/body/div[2]/div[4]/div[2]/div/div[3]/div[3]/table/tbody')
        for tmp_element in vSecurities.find_elements(By.TAG_NAME, 'tr'):
            tmp_element.find_elements(By.TAG_NAME, 'td')[self.f_findrelevantcolumns()].find_element(By.TAG_NAME, 'a').click()

    def f_nextpage(self):
        vPager = driver.find_element(By.XPATH, '/html/body/div[2]/div[4]/div[2]/div/div[3]/div[4]')
        vPager.find_element(By.CSS_SELECTOR, 'li.next').click()

    def downloadall(self):

        i = 1
        #intNumberPage = driver.find_element(By.XPATH, '/html/body/div[2]/div[4]/div[2]/div/div[3]/div[4]/ul').find_elements(By.TAG_NAME,'li')[-2].text
        intNumberPage = 2
        while i <= intNumberPage:

            time.sleep(0.5)
            self.downloadcurrentpage()
            self.f_nextpage()
            i += 1


Datacollector = SecurityType(document_type='Standalone prospectus')
Datacollector.f_search()
Datacollector.downloadall()




