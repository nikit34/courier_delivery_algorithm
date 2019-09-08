#!/usr/bin/env python
# coding: utf-8

from tqdm import tqdm
import pandas as pd
import json
import numpy as np


with open(r'contest_input.json', 'r') as read_file:
    data = json.load(read_file)

df_couriers = pd.DataFrame(data['couriers'])
df_depots = pd.DataFrame(data['depots'])
df_orders = pd.DataFrame(data['orders'])


df_orders['delivery_time'] = 10 + np.abs(df_orders['pickup_location_x'] - df_orders['dropoff_location_x']) + np.abs(df_orders['pickup_location_y'] - df_orders['dropoff_location_y'])
df_orders['profitable_trans'] = (df_orders['payment'] / df_orders['delivery_time'])
df_orders['profitable_trans'] =  (df_orders['profitable_trans'] + df_orders['profitable_trans'].min())


def distance_between_punches(loc1, loc2):
    dist = abs(loc1[0] - loc2[0]) + abs(loc1[1] - loc2[1])
    return dist

min_sort_order = df_orders.sort_values('dropoff_to', axis=0, ascending=True, inplace=False)
min_sort_order.reset_index(drop=True, inplace=True)
tmp_start = 0
delta_step = len(min_sort_order) // 20
min_row_location_between_courier_order = []


while delta_step != len(min_sort_order):
    min_tmp = float("inf")

    for i in tqdm(range(tmp_start , delta_step)):
        weight = min_sort_order['profitable_trans'][i]
        for j in range(len(df_couriers)):
            distance = distance_between_punches((df_couriers['location_x'][j], min_sort_order['pickup_location_x'][i]),(df_couriers['location_y'][j], min_sort_order['pickup_location_y'][i]))
            if min_tmp > distance * weight:
                min_tmp = distance * weight
                df_couriers['location_x'][j] = min_sort_order['pickup_location_x'][i]
                df_couriers['location_y'][j] = min_sort_order['pickup_location_y'][i]
                min_location_tmp_row = df_couriers.iloc[j,:]
                reset_j = j

        df_couriers['location_x'][reset_j] = min_sort_order['pickup_location_x'][i]
        df_couriers['location_y'][reset_j] = min_sort_order['pickup_location_y'][i]
        min_sort_order.drop([i])

        i+=1
        min_tmp = float("inf")
        min_row_location_between_courier_order.append(min_location_tmp_row)

        min_sort_order.loc[i,'dropoff_location_x'] = min_sort_order['pickup_location_x'][i]
        min_sort_order.loc[i,'dropoff_location_y'] = min_sort_order['pickup_location_y'][i]

    tmp_start += len(min_sort_order) // 20
    if ((len(min_sort_order) - delta_step) < len(min_sort_order)//20):
        delta_step = len(min_sort_order)
    else:
        delta_step += len(min_sort_order) // 20





res_counting = pd.DataFrame(min_row_location_between_courier_order)

print(res_counting)
