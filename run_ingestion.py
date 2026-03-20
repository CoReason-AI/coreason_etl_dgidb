import sys
import shutil
from pathlib import Path

# Force Python to look inside the "src" folder first
src_dir = Path(__file__).parent.absolute() / "src"
sys.path.insert(0, str(src_dir))

from coreason_etl_dgidb.pipeline import get_dlt_pipeline
from coreason_etl_dgidb.source import dgidb_source

if __name__ == "__main__":
    print("1. Dropping PostgreSQL state and wiping OS cache...")
    try:
        # Native dlt command to drop the database schema and memory
        get_dlt_pipeline().drop()
    except Exception:
        pass
        
    # Nuke the global hidden directory just to be safe
    shutil.rmtree(Path.home() / ".dlt", ignore_errors=True)

    print("2. Starting full DGIdb extraction...")
    # Re-initialize a brand new pipeline
    pipeline = get_dlt_pipeline()
    
    # Run the extraction!
    load_info = pipeline.run(dgidb_source())
    print(load_info)
