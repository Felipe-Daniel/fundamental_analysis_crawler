def clear(data):
    data = str(data)
    if '%' in data:
        data = float(data.replace('%', '')) / 100
    elif 'B' in data:
        data = float(data.replace('B', '')) * 1000
    data = str(data)
    return float(data
                 .replace(',', '')
                 .replace('(', '-')
                 .replace(')', '')
                 .replace('—', '0')
                 .replace('M', ''))


def beta_to_discount_rate(beta):
    try:
        if beta > 1.6:
            discount_rate = 0.09
        if beta < 1.6:
            discount_rate = 0.085
        if beta < 1.5:
            discount_rate = 0.08
        if beta < 1.4:
            discount_rate = 0.075
        if beta < 1.3:
            discount_rate = 0.07
        if beta < 1.2:
            discount_rate = 0.065
        if beta < 1.1:
            discount_rate = 0.06
        if beta < 0.8:
            discount_rate = 0.05
    except:
        discount_rate = 0.07
        print('no beta')
    return discount_rate


def intrinsic_value(
        cash_flow_ttm, net_income_ttm, debt, total_cash, eps_5y, discount_rate, shr_outstand):
    if eps_5y > 0.15:
        eps_3_10y = 0.15
    else:
        eps_3_10y = eps_5y

    pv_10y = 0
    intrinsic_value_list = []
    for cash_net in [cash_flow_ttm, net_income_ttm]:
        for i in range(1, 4):
            discount_factor = 1 / (1 + discount_rate) ** i
            cash_flow_projected = cash_net * ((1 + eps_5y) ** i)
            pv_10y += cash_flow_projected * discount_factor
        for i in range(4, 11):
            discount_factor = 1 / (1 + discount_rate) ** i
            cash_flow_projected = cash_net * ((1 + eps_5y) ** 3) * ((1 + eps_3_10y) ** (i - 3))
            pv_10y += cash_flow_projected * discount_factor

        intrinsic_value_list.append(pv_10y / shr_outstand
                                    - debt / shr_outstand
                                    + total_cash / shr_outstand)
    return intrinsic_value_list

