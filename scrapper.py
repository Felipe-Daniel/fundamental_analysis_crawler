from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from functions import *
import pandas_datareader.data as web
import datetime as dt
import time


def wait_id(element_id):
    element = WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.ID, element_id)))
    return element

def wait_text(element_text):
    element = WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.LINK_TEXT, element_text)))
    return element




stocks = input('Symbols(separeted by commas): ').upper().replace(" ", '').split(',')
failed_stocks = []
for symbol in stocks:
    # try:
    PATH = 'C:\chromedriver.exe'
    driver = webdriver.Chrome(PATH)
    stock_price = web.DataReader(symbol, 'yahoo', dt.date.today(), dt.date.today()).iloc[-1]['Close']
    driver.get(f'http://financials.morningstar.com/income-statement/is.html?t={symbol}')
    driver.implicitly_wait(60)

    # INCOME STATEMENT SECTION
    wait_id('menu_A').click()
    wait_text('Annual').click()
    revenue_row = wait_id("data_i1")
    net_income_row = wait_id('data_i80')
    net_income_ttm = clear(net_income_row.find_element(By.ID, 'Y_6').text)

    revenue_list = []
    for i in range(1, 7):
        revenue_list.append(clear(revenue_row \
                                  .find_element(By.ID, f'Y_{i}') \
                                  .text))
    net_income_list = []
    for i in range(1, 7):
        net_income_list.append(clear(net_income_row.find_element(By.ID, f'Y_{i}').text))
    try:
        interest_expense = clear(wait_id('data_i51') \
                                 .find_element(By.ID, 'Y_6').text)
    except Exception as e:
        print(f'symbol: {e}')
        continue

    # CASH FLOW SECTION
    cash_flow_link = wait_text('Cash Flow')
    cash_flow_link.click()
    time.sleep(2)
    cash_flow_row = wait_id('data_tts1')
    cash_flow_list = []
    for i in range(1, 7):
        cash_flow_list.append(clear(
            cash_flow_row.find_element(By.ID, f'Y_{i}').text))

    cash_flow_ttm = cash_flow_list[-1]

    # BALANCE SHEET SECTION
    balance_sheet_link = wait_text('Balance Sheet')
    balance_sheet_link.click()
    time.sleep(3)
    # CONSEVATIVE DEBT
    total_current_assets = wait_id('data_ttg1') \
        .find_element(By.ID, f'Y_5').text
    total_current_liabilites = wait_id('data_ttgg5') \
        .find_element(By.ID, f'Y_5').text
    current_ratio = (clear(total_current_assets) / clear(total_current_liabilites))  # THIS
    debt_to_equity_ratio = []  # THIS
    total_liabilites_row = wait_id('data_ttg5')
    total_stockholders_equity_row = wait_id('data_ttg8')
    for i in range(1, 6):
        total_liabilites = clear(total_liabilites_row \
                                 .find_element(By.ID, f'Y_{i}').text)
        total_stockholders_equity = clear(total_stockholders_equity_row \
                                          .find_element(By.ID, f'Y_{i}').text)
        debt_to_equity_ratio.append(clear(total_liabilites) / clear(total_stockholders_equity))
    debt_servicing_ratio = interest_expense / cash_flow_ttm

    # Quarterly
    wait_id('menu_A').click()
    wait_text('Quarterly').click()
    time.sleep(2)
    try:
        short_term_debt = clear(wait_id('data_i41') \
                                .find_element(By.ID, 'Y_5').text)
    except Exception as e:
        print(f'Short Term Debt: {e}')
        short_term_debt = 0
    try:
        long_term_debt = clear(wait_id('data_i50') \
                               .find_element(By.ID, 'Y_5').text)
    except Exception as e:
        print(f'Long Term Debt: {e}')
        long_term_debt = 0
    debt = short_term_debt + long_term_debt

    total_cash = clear(wait_id('data_ttgg1') \
                       .find_element(By.ID, 'Y_5').text)
    wait_id('menu_A').click()
    wait_text('Annual').click()

    # KEY RATIOS
    key_ratios_link = wait_text('Key Ratios')
    key_ratios_link.click()
    time.sleep(2)
    return_on_equity = []


    return_on_equity_row = driver.find_elements(By.TAG_NAME, 'table')[2] \
        .find_elements(By.TAG_NAME, 'tr')[12]
    return_on_equity_elements = return_on_equity_row.find_elements(By.TAG_NAME, 'td')
    for i in return_on_equity_elements:
        return_on_equity.append(i.text)
    # Finviz
    driver.get(f'https://finviz.com/quote.ashx?t={symbol}')
    table = driver.find_elements(By.CLASS_NAME, 'snapshot-table2')[0]
    eps_5y = clear(table \
                   .find_elements(By.TAG_NAME, 'tr')[5] \
                   .find_elements(By.TAG_NAME, 'td')[5].text)

    beta = clear(table \
                 .find_elements(By.TAG_NAME, 'tr')[6] \
                 .find_elements(By.TAG_NAME, 'td')[11].text)
    discount_rate = beta_to_discount_rate(beta)
    peg = table \
        .find_elements(By.TAG_NAME, 'tr')[2] \
        .find_elements(By.TAG_NAME, 'td')[3].text
    shr_outstand = clear(table \
                         .find_elements(By.TAG_NAME, 'tr')[0] \
                         .find_elements(By.TAG_NAME, 'td')[9].text)
    driver.quit()
    intrinsic_value_list = intrinsic_value(
        cash_flow_ttm=cash_flow_ttm,
        net_income_ttm=net_income_ttm,
        debt=debt,
        total_cash=total_cash,
        eps_5y=eps_5y,
        discount_rate=discount_rate,
        shr_outstand=shr_outstand)
    print("\n" + symbol)
    print('1. Consistently Increacing Sales, Earnings and Cash Flow')
    print(f'Revenue: {revenue_list}')
    print(f'Net Income: {net_income_list}')
    print(f'Cash Flow: {cash_flow_list}')
    print('\n')
    print('2. Positive Growth Rate')
    print(f'EPS_5y: {eps_5y} - {eps_5y > 0}')
    print('\n')
    print('3. Sustenable Competitive Advantage(MOAT)')
    print('Is it a brand monopoly?')
    print('High gross profit margins above industry?')
    print('High Barriers to entry? ')
    print('Huge economys of scale?')
    print('Networking effect?')
    print('High swiching cost?')
    print('\n')
    print('4. High and Consistent Return on Equity')
    print(f'ROE: {return_on_equity}')
    print('\n')
    print('5. Conservative Debt')
    print(f'Current Ratio(>1): {current_ratio} - {current_ratio > 1}')
    print(f'Consistent or falling Debt to Equity Ratio: {debt_to_equity_ratio}')
    print(f'Debt Servicing Ratio(<30%): {debt_servicing_ratio} - {debt_servicing_ratio < 0.30}')
    print('\n')
    print('6. Intrinsic Value')
    print(f'PEG: {peg}')
    print(f'Instrisic Value: {intrinsic_value_list[0]} - {(stock_price / intrinsic_value_list[0]) < 1.2}')
    print(f'Net Income Instrisic Value: {intrinsic_value_list[1]} - {(stock_price / intrinsic_value_list[1]) < 1.2}')
    print(f'Stock Price: {stock_price}')
    success = []
    if (not eps_5y > 0 or not current_ratio > 1 or not debt_servicing_ratio < 0.30 or not (stock_price /
                                                                                           intrinsic_value_list[
                                                                                               0]) < 1.2):
        print('\n Stock FAILED')
        failed_stocks.append(symbol)
    else:
        success.append(symbol)
# except Exception as e:
#     print(e)
#     failed_stocks.append(symbol)
print(failed_stocks)
print(success)
