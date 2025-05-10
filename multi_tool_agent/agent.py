import pandas as pd
from pathlib import Path
from google.adk.agents import Agent

# Based on provided dataset
MAX_HSN_CODE_LENGTH=8
MIN_HSN_CODE_LENGTH = 2
# Load dataset at import time
base_dir = Path(__file__).parent
csv_path = base_dir / "HSN.csv"
_hsn_df = pd.read_csv(csv_path, dtype={"HSNCode": str})

# Normalize column names and data
_hsn_df.columns = _hsn_df.columns.str.strip()
_hsn_df["HSNCode"] = _hsn_df["HSNCode"].str.strip()
_hsn_df["Description"] = _hsn_df["Description"].str.strip()

_hsn_map = dict(zip(_hsn_df["HSNCode"], _hsn_df["Description"]))
# _valid_hsn_codes = set(_hsn_df["HSNCode"])



def validate_HSNCode(code_str: str) -> dict:
 

    """Checks if provided HSN code is valid based on the master csv dataset.

    Args:
        code (str): The HSN code to check if it is present in the dataset.

    Returns:
        dict: status and result or error msg.
    """

    code_str = code_str.strip()
    if not (MIN_HSN_CODE_LENGTH <= len(code_str) <= MAX_HSN_CODE_LENGTH):
        return {
            "status": "error",
            "message": (
                f"HSN code '{code_str}' must be between "
                f"{MIN_HSN_CODE_LENGTH} and {MAX_HSN_CODE_LENGTH} digits."
            )
        }
    if not code_str.isdigit():
        return {
            "status": "error",
            "message": f"HSN code '{code_str}' contains non-numeric characters."
        }
    if code_str in _hsn_map:
        return {
            "status": "success",
            "message": f"HSN code {code_str} is valid.",
            "description": _hsn_map[code_str]
        }
    else:
        return {
            "status": "error",
            "message": f"HSN code {code_str} not found."
        }


root_agent = Agent(
    name="HSN_validator_agent",
    model="gemini-2.0-flash",
    description=(
        "Agent to check and validate HSN codes from a master dataset csv file. Return descriptions of valid HSN codes in tabular format."
    ),
    instruction=(
        "You are a helpful agent who can check HSN codes given by the user and tell if it is present in master dataset csv file. Also return the description of valid HSN codes in tabular format. You can validate multiple HSN codes at a time."
    ),
    tools=[validate_HSNCode],
)