# curation_corp_dev.pulse_customer_director
import os
from datetime import datetime

import numpy as np
import pandas as pd
import warnings

warnings.filterwarnings("ignore")


class utility:
    def scenarios(self, name, df_mob1_mob2, df_pass_age, df_scenario3, df_del):

        ## Secenario 1 -----------------------------------------------------------------------------------------------------------------------
        ls = [
            "grpcis",
            "director_name",
            "passport_number",
            "Age",
            "Group",
            "fuzzy_grp_nms",
        ]
        ubaid = df_mob1_mob2.loc[
            (df_mob1_mob2["director_name"].str.startswith("UBAID"))
            & (df_mob1_mob2["grpcis"] == "010668634")
        ]

        # ALL names
        sear_for = [
            "RAJEEV KU",
            "RAJEEV NAI",
            "VICKY",
            "HARSHA",
            "YVONNE",
            "RICHARD FAR",
            "ZENA M",
            "JOCELYN ",
        ]
        all_nms = df_mob1_mob2.loc[
            df_mob1_mob2["director_name"].str.contains("|".join(sear_for))
        ]

        all_nms = pd.concat([all_nms, ubaid])

        f = (
            pd.merge(df_mob1_mob2, all_nms, indicator=True, how="outer")
            .query('_merge=="left_only"')
            .drop("_merge", axis=1)
        )

        mask = (
            (f["passport_number"] == "")
            & (f["visa_no"] == "")
            & (f["Age"] == "")
            & ((f["mobile_1_new"] != "") | (f["mobile_2_new"] != ""))
        )
        only_mobile = f.loc[mask]

        # director name, mobile_1, mobile_2
        final_set_scn1 = pd.concat([only_mobile, all_nms])
        print(f"After Scenario 1: {final_set_scn1.shape}")

        ## Scenario 2 -----------------------------------------------------------------------------------------------------------------------
        # ALL names
        mask = (df_pass_age["passport_number"] != "") | (df_pass_age["Age"] != "")
        sear_for = [
            "YOUSEF",
            "KHALED",
            "ZAYED",
            "ZEINA",
            "ABDULKADER",
            "MANSOUR",
            "BUTHAINA",
            "SAMIR",
            "MAJED",
            "AMER TAHER",
            "NASER BUTTI",
            "NASER ZAKARIYA",
        ]
        all_nms = df_pass_age.loc[
            (df_pass_age["director_name"].str.contains("|".join(sear_for))) & mask
        ]

        f = (
            pd.merge(df_pass_age, all_nms, indicator=True, how="outer")
            .query('_merge=="left_only"')
            .drop("_merge", axis=1)
        )

        mask = (
            (f["mobile_1"] == "") & (f["mobile_2"] == "") & (f["visa_no"] == "")
        ) & ((f["passport_number"] != "") | (f["Age"] != ""))
        # display(f.loc[mask].shape)
        only_pass_age = f.loc[mask]
        final_set_scn2 = pd.concat([only_pass_age, all_nms])
        print(f"After Scenario 2: {final_set_scn2.shape}")

        ## Subset from scenario_1 and scenario_2 ----------------------------------------------------------------------------------------------
        scn1_scn2 = pd.concat([final_set_scn1, final_set_scn2])
        print(f"Combining SC1 and SC2: {scn1_scn2.shape}")

        df_temp = df_scenario3.loc[
            ~(
                (df_scenario3.director_name.isin(scn1_scn2["director_name"]))
                & (df_scenario3.id.isin(scn1_scn2["id"]))
            ),
            :,
        ]

        ## Final set
        df_final = pd.concat([scn1_scn2, df_temp])

        dfs = []
        global combined
        for name, group in df_final.groupby("grpcis"):
            dfs.append(group)

        df_combined = pd.concat(dfs)
        m = (
            (df_combined["passport_number"] == "")
            & (df_combined["Age"] == "")
            & (df_combined["visa_no"] == "")
            & (df_combined["mobile_1"] == "")
            & (df_combined["mobile_2"] == "")
            & (df_combined["national_id_number"] == "")
        )
        df_combined["fuzzy_grp_nms_f"] = np.where(
            m, df_combined["director_name_new"], df_combined["fuzzy_grp_nms"]
        )

        df_combined = df_combined.loc[:, ~df_combined.columns.str.endswith("_new")]
        df_combined.drop(["fuzzy_grp_nms"], axis=1, inplace=True)

        #----------------------------------------------------------------------
        col = [
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

        df_combined_f = pd.concat([df_combined, df_del[col]])
        #-----------------------------------------------------------------------
        print(f"Final_Set: {df_combined_f.shape}")
        name = "persona_matching"
        print(name)
        # self.export_csv(name, df_combined)
        return df_combined_f

    def export_csv(self, name, df_final, export_path="../persona-app/Outputs"):

        csv_file = (
            name
            + "_"
            + "fuzzy_out_"
            + str(datetime.now().strftime("%Y%m%d_%H%M%S"))
            + ".csv"
        )
        print(name)
        pth = os.path.join(export_path, csv_file)
        print(pth)
        return df_final.to_csv(pth, index=False)
