import re
from datetime import date
import numpy as np
import pandas as pd
import warnings
from sqlalchemy import create_engine

warnings.filterwarnings("ignore")
import logging
import sqlalchemy
import impala.sqlalchemy
import impala.hiveserver2

impala.hiveserver2.HiveServer2Cursor.lastrowid = None
impala.sqlalchemy.ImpalaDialect.supports_multivalues_insert = True


class help:
    def read_data(self, connection_string: str, query: str):

        engine = create_engine(connection_string)
        with engine.connect() as conn:
            df = pd.read_sql_query(query, con=conn)
        return df

    def rmv_junk_data(self, df):
        mask = (df['director_name'].str.len()<3)
        df1 = df.loc[mask]
        df2 = df.loc[~mask]
        print(f'Junk Data: {df1.shape}; Cleaned: {df2.shape}')
        return df2, df1



    def ingest_data(self, sc_nm, df, table, connection_string: str, command):
        engine = create_engine(connection_string)
        conn = engine.raw_connection()
        cursor = conn.cursor()
        cursor.execute(command)
        print("table dropped...")
        conn.commit()
        conn.close()
        print("Insertion started")
        logging.getLogger("sqlalchemy.engine").setLevel(logging.INFO)

        # Execution
        df.to_sql(
            table, engine, schema=sc_nm, index=False, chunksize=5000, method="multi"
        )

    def age(self, born):
        born = born.date()
        #     print(born)
        today = date.today()
        return (
            today.year - born.year - ((today.month, today.day) < (born.month, born.day))
        )

    def utili(self, s):
        res = re.search("\(([^)]+)", s)
        if res:
            return res.group(1)
        else:
            return "-1"

    def clean(self, df):

        ls = [
            "grpcis",
            "customer_no",
            "director_name",
            "passport_number",
            "dob",
            "visa_no",
            "mobile_1",
            "mobile_2",
            "e_mail",
            "national_id_number",
        ]
        pd.set_option("display.float_format", lambda x: "%.3f" % x)
        df = df[ls]

        for i in ["passport_number", "e_mail"]:
            df[i].fillna("", inplace=True)
            df[i].fillna("", inplace=True)

        df["visa_no"].fillna("", inplace=True)
        df["visa_no"] = df["visa_no"].replace(to_replace=r"/", value="", regex=True)
        df["visa_no"] = df["visa_no"].replace("\.0", "", regex=True)

        for i in ["mobile_1", "mobile_2", "national_id_number"]:
            df[i].fillna("", inplace=True)

        df["dob"] = pd.to_datetime(df["dob"], errors="coerce")
        df["dob"].dt.strftime("%Y-%m-%d")
        df["Age"] = df["dob"].apply(self.age)
        df["Age"] = df["Age"].fillna(0)
        df["Age"] = df["Age"].astype(int)
        mask = (df["Age"] <= 15) | (df["Age"] == 0)
        df.loc[mask, "Age"] = -1
        df["Age"] = df["Age"].astype(str)
        df.loc[(df["Age"] == "-1"), "Age"] = ""
        df.drop(["dob"], axis=1, inplace=True)

        # ---------------------------------------------------------------------------------
        special = '[(_:./?,$#%\=@*")]'
        df["director_name_new"] = df["director_name"].str.replace(special, "")

        for i in df.columns:
            if not i in ("grpcis", "director_name", "director_name_new"):
                df[i + "_new"] = df[i].apply(lambda x: "_" + str(x) if x != "" else x)

        nm = [
            "MRSSNEHAL DESAI",
            "MRSALPANA",
            "MRSAMY PEL",
            "MRSHARSHADA RAJE",
            "MRSAYESHA HASSAN ABDULKARIM ALDARAKEI",
            "MRSPADMA RAMESH",
        ]
        df["director_name_new"] = df["director_name_new"].apply(
            lambda x: x[3:] if x in nm else x
        )
        df["director_name_new"] = df["director_name_new"].str.replace("^MR", "")

        df["director_name_new"] = df["director_name_new"].str.replace("^MRS ", "")

        df["director_name_new"] = df["director_name_new"].str.replace("^MR ", "")

        df["director_name_new"] = df["director_name_new"].str.replace("^MS ", "")

        df["director_name_new"] = df["director_name_new"].str.replace("^MS", "")

        df["director_name_new"] = df["director_name_new"].str.replace("^HE ", "")

        df["director_name_new"] = df["director_name_new"].str.replace("^HH", "")
        df["director_name_new"] = df["director_name_new"].str.replace("^S ", "")
        df["director_name"] = df["director_name"].str.strip()
        df["id"] = df.index + 1

        print("After cleaning:", df.shape)

        return df
