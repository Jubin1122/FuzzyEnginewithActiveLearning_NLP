import re
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sparse_dot_topn import awesome_cossim_topn
import warnings

warnings.filterwarnings("ignore")
from utilities.helper import help

import logging

logger = logging.getLogger(__file__)
logging.basicConfig(level=logging.DEBUG)

#   https://github.com/ing-bank/sparse_dot_topn


class FuzzyUtility:
    def __init__(
        self,
        scn,
        df,
        name,
        columns_to_group,
        match_threshold,
        ngram_remove=r"[,-./]",
        ngram_length=3,
    ):
        self.df = df
        self.group_lookup = {}
        self._scn = scn
        self._name = name
        self._grp = columns_to_group
        self._match_threshold = match_threshold
        self._ngram_remove = ngram_remove
        self._ngram_length = ngram_length

    def get_column(self, columns_to_group):
        if "".join(columns_to_group) in self.df.columns:
            return "".join(columns_to_group)
        else:
            self.df["FuzzyUtilityGrouper"] = (
                self.df[columns_to_group.pop(0)]
                .astype(str)
                .str.cat(self.df[columns_to_group].astype(str))
            )
            return "FuzzyUtilityGrouper"

    def ngrams_analyzer(self, string):
        string = re.sub(self._ngram_remove, r"", string)
        ngrams = zip(*[string[i:] for i in range(self._ngram_length)])
        return ["".join(ngram) for ngram in ngrams]

    def get_tf_idf_matrix(self, vals):
        try:
            vectorizer = TfidfVectorizer(analyzer=self.ngrams_analyzer)
            # return vectorizer.fit_transform(vals)
            return vectorizer.fit_transform(vals)
        except Exception as e:
            # logger.info(vals)
            logger.error(str(e))

    def get_cosine_matrix(self, vals):
        tf_idf_matrix = self.get_tf_idf_matrix(vals)
        return awesome_cossim_topn(
            tf_idf_matrix, tf_idf_matrix.transpose(), vals.size, self._match_threshold
        )

    def find_group(self, y, x):
        if y in self.group_lookup:
            return self.group_lookup[y]
        elif x in self.group_lookup:
            return self.group_lookup[x]
        else:
            return None

    def add_vals_to_lookup(self, group, y, x):
        self.group_lookup[y] = group
        self.group_lookup[x] = group

    def add_pair_to_lookup(self, row, col):
        group = self.find_group(row, col)
        if group is not None:
            self.add_vals_to_lookup(group, row, col)
        else:
            self.add_vals_to_lookup(row, row, col)

    def set_ngram_remove(self, ngram_remove):
        self._ngram_remove = ngram_remove

    def set_ngram_length(self, ngram_length):
        self._ngram_length = ngram_length

    def set_match_threshold(self, match_threshold):
        self._match_threshold = match_threshold

    def get_column_grp(self, df_g, col_group):
        if "".join(col_group) in df_g.columns:
            return "".join(col_group)
        else:
            df_g["FuzzyUtilityGrouper"] = (
                df_g[col_group.pop(0)].astype(str).str.cat(df_g[col_group].astype(str))
            )
            return "FuzzyUtilityGrouper"

    def build_group_lookup(self, df_g):

        grp = [
            "director_name",
            "passport_number",
            "visa_no",
            "mobile_1",
            "mobile_2",
            "e_mail",
            "national_id_number",
            "Age",
        ]
        if self._scn == "scenario_1":
            grp = ["director_name_new", "mobile_1_new", "mobile_2_new"]

        elif self._scn == "scenario_2":
            grp = ["director_name_new", "passport_number_new", "Age_new"]

        elif self._scn == "scenario_3":
            grp = [
                "director_name_new",
                "Age_new",
                "passport_number_new",
                "visa_no_new",
                "national_id_number_new",
                "mobile_1_new",
            ]

        # print(f"{self._name}: {self._grp}")
        # print(f"Manual: {grp}")
        clm = self.get_column_grp(df_g, grp)
        vals = df_g[clm].unique().astype("U")
        # logger.info(vals)

        # print("Building the TF-IDF, Cosine & Coord matrices...")
        coord_matrix = self.get_cosine_matrix(vals).tocoo()

        # print("Building the group lookup...")
        for row, col in zip(coord_matrix.row, coord_matrix.col):
            if row != col:
                self.add_pair_to_lookup(vals[row], vals[col])

        return df_g, clm

    def add_grouped_column_to_data(self, df_g, clm, column_name="Group"):
        # print("Adding grouped columns to data frame...")
        df_g[column_name] = df_g[clm].map(self.group_lookup).fillna(df_g[clm])
        return df_g

    def run(self, column_name="Group"):
        dfs = []
        global combined
        for name, group in self.df.groupby("grpcis"):
            out, clm = self.build_group_lookup(group)
            df_g = self.add_grouped_column_to_data(out, clm, column_name)
            dfs.append(df_g)

        combined = pd.concat(dfs)
        print("Ready for export")
        return self.filter_df_for_export(combined)

    def filter_df_for_export(self, df_g):

        df_g["fuzzy_grp_nms"] = df_g["Group"].str.split("_").str[0]
        df_fn = df_g.copy()

        return (
            df_fn.drop(columns=["FuzzyUtilityGrouper"])
            if "FuzzyUtilityGrouper" in df_fn.columns
            else df_fn
        )


def read_csv(
    scn,
    df,
    name,
    columns_to_group,
    match_threshold,
    ngram_remove=r"[,-./]",
    ngram_length=3, 
):

    obj = help()
    df_all = obj.clean(df)

    return FuzzyUtility(
        scn, df_all, name, columns_to_group, match_threshold, ngram_remove, ngram_length
    )
