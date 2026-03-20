# run_dbt.py
import sys
import pydantic.v1.fields
from pydantic.v1.errors import ConfigError
from dotenv import load_dotenv

# 1. Load the .env file into the OS environment so dbt can read your credentials
load_dotenv()

# 2. Patch Pydantic V1 for Python 3.14 compatibility
original_set_default = pydantic.v1.fields.ModelField._set_default_and_type

def patched_set_default_and_type(self):
    try:
        original_set_default(self)
    except ConfigError as e:
        if "default_factory" in str(e) and self.default_factory is not None:
            fallback_type = type(self.default_factory())
            self.type_ = fallback_type
            self.outer_type_ = fallback_type
        else:
            raise

pydantic.v1.fields.ModelField._set_default_and_type = patched_set_default_and_type

if __name__ == "__main__":
    # 3. Boot the dbt CLI
    from dbt.cli.main import cli
    sys.exit(cli())
