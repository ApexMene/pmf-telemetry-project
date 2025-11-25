import fastf1
import polars as pl
from pathlib import Path


def load_data_sample():
    try:
        BASE_DIR = Path(__file__).resolve().parents[2]
        cache_dir = BASE_DIR / "cache"
        data_dir = BASE_DIR / "data"

        cache_dir.mkdir(exist_ok=True)
        data_dir.mkdir(exist_ok=True)

        fastf1.Cache.enable_cache(str(cache_dir))

        session = fastf1.get_session(2020, "Tuscan", "Q")
        session.load()

        driver = "LEC"
        lap = session.laps.pick_driver(driver).pick_fastest()
        telemetry = lap.get_telemetry()

        df = pl.DataFrame(
            telemetry[["Time", "Speed", "RPM", "nGear", "Throttle", "Brake", "X", "Y", "Z"]]
        )

        df = df.with_columns(
            [
                (pl.col("Time").dt.total_milliseconds() / 1000).alias("Time_Sec"),
                (pl.col("RPM") * 1.1).alias("RPM"),
            ]
        )

        parquet_path = data_dir / "mugello_telemetry_2020_f1_LEC.parquet"
        df.write_parquet(parquet_path)

        print(f"Dataset salvato in: {parquet_path}")
        return parquet_path

    except Exception as e:
        print(f"Error during downloading dataset: {e}")
        return None

