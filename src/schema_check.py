import pandas as pd

class BaseSchema:

    def __init__(self, df: pd.DataFrame):
        self.df=df

    def check_schema(self):
        return {col: str(dtype) for col, dtype in self.df.dtypes.items()}

    def compare_schema(self, new_df: pd.DataFrame):
        current_schema = self.check_schema()
        new_schema= {col: str(dtype) for col, dtype in new_df.dtypes.items()}
        added_columns = {col: dtype for col, dtype in new_schema.items() if col not in current_schema}
        removed_columns = {col: dtype for col, dtype in current_schema.items() if col not in new_schema}
        

