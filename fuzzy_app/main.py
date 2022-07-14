from datetime import datetime
import os
from fuzzy.test_group import run_fuzz_utility
from utilities.helper import help
from utilities.hybrid_app import utility
import logging
import argparse


logger = logging.getLogger(__file__)
logging.basicConfig(level=logging.DEBUG)

if __name__ == "__main__":

    # CURATION_CORP_DEV.PERSONA_CUSTOMER_DETAILS_TEMP4
    parser = argparse.ArgumentParser()
    parser.add_argument("--table_name", type=str, help="input table name", dest="table")
    parser.add_argument(
        "--schema_name", type=str, help="input schema name", dest="schema"
    )
    parser.add_argument(
        "--staging_table", type=str, help="input staging table name", dest="stg_tbl"
    )
    parser.add_argument(
        "--staging_schema", type=str, help="input staging schema name", dest="stg_sch"
    )

    try:
        args = parser.parse_args()
        table_name = args.table
        schema_name = args.schema
        staging_table = args.stg_tbl
        staging_schema =  args.stg_sch

        # table_name = "PERSONA_CUSTOMER_DETAILS_TEMP4"
        # schema_name = "curation_corp_dev"
        # staging_table = "PERSONA_FUZZY_OUTPUT_1"
        # staging_schema =  "curation_corp_dev"


        logger.info(f"table_name: {table_name}")
        logger.info(f"schema_name: {schema_name}")
        logger.info(f"staging_table: {staging_table}")
        logger.info(f"staging_schema: {staging_schema}")

    except Exception as e:
        raise (e)

    # tb_name = "PERSONA_CUSTOMER_DETAILS_TEMP4"
    # sc_nm = "curation_corp_dev"
    tb_name = table_name
    sc_nm = schema_name
    name = "persona_customer_details_temp4"
    scn = ["scenario_1", "scenario_2", "scenario_3"]
    grps = [
        ["director_name_new", "mobile_1_new", "mobile_1_new"],
        ["director_name_new", "passport_number_new", "Age_new"],
        [
            "director_name_new",
            "Age_new",
            "passport_number_new",
            "visa_no_new",
            "national_id_number_new",
            "mobile_1_new",
        ],
    ]
    # df = run_fuzz_utility_1(scn, tb_name, name, 0.76)
    # start = datetime.now()
    print("Fuzzy Engine started....")
    df_sc1, df_sc2, df_sc3, df_del = run_fuzz_utility(scn, sc_nm, tb_name, name, grps, 0.76)
    obj = utility()
    hp = help()
    print("Data Curation started....")
    df_fuzz = obj.scenarios(name, df_sc1, df_sc2, df_sc3, df_del)
    # print("Export file to local....")
    obj.export_csv('Pers_loc',df_fuzz)
    print("Ingestion has started...")
    conn_string = os.environ["hive_secret"]
    # table_nm = "PERSONA_FUZZY_OUTPUT_1"
    # create the table but first drop if it already exists
    command = f"DROP TABLE IF EXISTS {staging_schema}.{staging_table}"

    hp.ingest_data(staging_schema, df_fuzz, staging_table, conn_string, command)
    logger.info("Insertion Completed....")
    # stop = datetime.now()

    # print("Time: ", stop - start)
    # logger.info("Time: ", stop - start)

