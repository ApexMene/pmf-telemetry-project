import polars as pl
from src.config.settings import config_pmf_object as config_pmf

DATA_PATH = config_pmf.DATA_PATH
REV_LIMIT_RPM = config_pmf.REV_LIMIT_RPM
GEAR_OFFSET = config_pmf.GEAR_OFFSET

def load_dataset():
    if not DATA_PATH.exists():
        raise FileNotFoundError(f"Data nto found in: {DATA_PATH}")
    
    df = pl.read_parquet(DATA_PATH)
    
    # business logic adottate nel notebook di eda e preprocessing
    df = df.with_columns([
        pl.col("RPM").clip(0, REV_LIMIT_RPM),
        (pl.col("nGear") + GEAR_OFFSET).clip(1,6).alias("nGear")
    ])
    
    return df
    

