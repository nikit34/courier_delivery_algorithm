#!/usr/bin/env python
# coding: utf-8

from tqdm import tqdm
import pandas as pd
import json
import numpy as np
import math

contest = r'contest'
hard = r'hard'
simple = r'simple'

tmp_file = contest

with open(tmp_file + r'_input.json', 'r') as read_file:
    data = json.load(read_file)

df_couriers = pd.DataFrame(data['couriers'])
df_depots = pd.DataFrame(data['depots'])
df_orders = pd.DataFrame(data['orders'])

df_couriers.loc[:, 'flag_product'] = False

df_depots = df_depots.rename(columns={"location_x": "pickup_location_x", "location_y": "pickup_location_y"})
df_orders = pd.concat([df_orders, df_depots], sort=True)

df_orders['delivery_time'] = 10 + np.abs(df_orders['pickup_location_x'] - df_orders['dropoff_location_x']) + np.abs(df_orders['pickup_location_y'] - df_orders['dropoff_location_y'])
df_orders['profitable_trans'] = (df_orders['payment'] / df_orders['delivery_time'])


def distance_between_punches(loc1, loc2):
    dist = abs(loc1[0] - loc2[0]) + abs(loc1[1] - loc2[1])
    return dist


min_sort_order = df_orders.sort_values('pickup_to', axis=0, ascending=True, inplace=False)
min_sort_order.reset_index(drop=True, inplace=True)
tmp_start = 0
delta_step = math.floor(len(min_sort_order) * 0.2)
res = pd.DataFrame(None, columns=['courier_id', 'action','order_id','point_id'])

while delta_step != len(min_sort_order):
    min_tmp = float("inf")

    for i in tqdm(range(tmp_start, delta_step)):
        weight = min_sort_order.loc[i, 'profitable_trans']

        for j in range(len(df_couriers)):
            distance = distance_between_punches((df_couriers.loc[j, 'location_x'], min_sort_order.loc[i, 'pickup_location_x']),(df_couriers.loc[j, 'location_y'], min_sort_order.loc[i, 'pickup_location_y']))

            if min_tmp > distance / weight:
                min_tmp = distance / weight
                df_couriers.loc[j, 'location_x'] = min_sort_order.loc[i, 'pickup_location_x']
                df_couriers.loc[j, 'location_y'] = min_sort_order.loc[i, 'pickup_location_y']

                if df_couriers.loc[j,'flag_product'] == False:
                    res_tmp_act = 'dropoff'
                    df_couriers.loc[j, 'flag_product'] = True
                else:
                    res_tmp_act = 'pickup'
                    df_couriers.loc[j, 'flag_product'] = False

                res.loc[len(res),['courier_id', 'action','order_id','point_id']] = [df_couriers.loc[j, 'courier_id'], res_tmp_act, min_sort_order.loc[i, 'order_id'], min_sort_order.loc[i, 'point_id']]
                reset_j = j

        df_couriers.loc[reset_j, 'location_x'] = min_sort_order.loc[i, 'pickup_location_x']
        df_couriers.loc[reset_j, 'location_y'] = min_sort_order.loc[i, 'pickup_location_y']
        min_sort_order.drop([i])

        min_tmp = float("inf")

        min_sort_order.loc[i,'dropoff_location_x'] = min_sort_order.loc[i, 'pickup_location_x']
        min_sort_order.loc[i,'dropoff_location_y'] = min_sort_order.loc[i, 'pickup_location_y']


    tmp_start += math.floor(len(min_sort_order) * 0.2)
    if ((len(min_sort_order) - delta_step) <  math.ceil(len(min_sort_order) * 0.2)):
        delta_step = len(min_sort_order)
    else:
        delta_step += math.floor(len(min_sort_order) * 0.2)


res.to_json(tmp_file + r'_output.json', orient='records')
print(res)
