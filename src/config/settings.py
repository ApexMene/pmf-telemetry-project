from pathlib import Path
import os


class ConfigurationPMF():
    PROJECT_ROOT = Path(__file__).parent.parent.parent
    DATA_PATH = PROJECT_ROOT / "data" / os.getenv("DATA_PATH","mugello_telemetry_2020_f1_LEC.parquet")
    
    # motostudent regulation 2025
    REV_LIMIT_RPM = int(os.getenv("REV_LIMIT_RPM", 14_000)) # Art. C.8.1.2
    MIN_BRAKE_SPEED = int(os.getenv("MIN_BRAKE_SPEED", 80)) # Art. F.12.2.1
    
    # adapters
    GEAR_OFFSET = int(os.getenv("GEAR_OFFSET", -2)) #adattamento f1 -> moto


config_pmf_object = ConfigurationPMF()