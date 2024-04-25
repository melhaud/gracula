from pathlib import Path

import pandas as pd

UPLOAD_FOLDER = "uploads"  # TODO use pathlib instead
OUTPUT_FOLDER = "outputs"
ALLOWED_PAPER_EXTENSIONS = {".pdf"}
ALLOWED_CONFIG_EXTENSIONS = {".json"}
ERROR_MESSAGE_REJECT_EXTENSION = (
    "{} has wrong extension {}, it will be ignored. see list of allowed formats: {}"
)


class InvalidFileExtension(Exception):
    """Raised when uploaded file is rejected due to invalid format."""


def upload_file_or_reject(uploaded_file, upload_folder) -> None:
    name = uploaded_file.name
    if (ext := Path(name).suffix) in ALLOWED_PAPER_EXTENSIONS:
        with open(upload_folder / name, "wb") as f:
            f.write(uploaded_file.read())
    else:
        raise InvalidFileExtension(
            ERROR_MESSAGE_REJECT_EXTENSION.format(name, ext, ALLOWED_PAPER_EXTENSIONS)
        )


def prepare_results_dataframe(output_folder, **kwargs) -> None:
    _ = kwargs
    # TODO: replace after having a data processing chain
    result_df = pd.read_csv(output_folder / "result.csv")
    return result_df
