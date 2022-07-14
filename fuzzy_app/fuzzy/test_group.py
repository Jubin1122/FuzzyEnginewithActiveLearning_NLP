import numpy as np
import pandas as pd
import os
from fuzzy.fuzzy_match_algo import read_csv
from utilities.helper import help
import warnings
import logging

logger = logging.getLogger(__file__)

warnings.filterwarnings("ignore")


def run_fuzz_utility(scn, sc_nm, tb_name, name, grps, match_threshold):

    obj = help()

    conn_string = os.environ["hive_secret"]
    query_str = f"select grpcis, customer_no, director_name, passport_number, dob, visa_no, mobile_1, mobile_2, e_mail, national_id_number from {sc_nm}.{tb_name}"
    logger.info("Reading data from hive...")
    df_fn = obj.read_data(query=query_str, connection_string=conn_string)
    df_f, df_del = obj.rmv_junk_data(df_fn)
    logger.info(f"Loaded Data: {df_f.shape}")
    logger.info("Completed.")

    ds = []
    for i in range(len(scn)):

        if scn[i] == "scenario_1":
            print('Scenario_1: ["director_name_new", "mobile_1_new", "mobile_2_new"]')
            grp = grps[i]
            fuzz_obj = read_csv(scn[i], df_f, name, grp, match_threshold)
            output = fuzz_obj.run()
            ds.append(output)

        elif scn[i] == "scenario_2":
            print('Scenario_2: ["director_name_new", "passport_number_new", "Age_new"]')
            grp = grps[i]
            fuzz_obj = read_csv(scn[i], df_f, name, grp, match_threshold)
            output = fuzz_obj.run()
            ds.append(output)

        elif scn[i] == "scenario_3":
            print(
                'Scenario_3: ["director_name_new","Age_new","passport_number_new","visa_no_new","national_id_number_new","mobile_1_new"]'
            )
            grp = grps[i]
            fuzz_obj = read_csv(scn[i], df_f, name, grp, match_threshold)
            output = fuzz_obj.run()
            ds.append(output)

    df_sc1, df_sc2, df_sc3 = ds

    return df_sc1, df_sc2, df_sc3, df_del
