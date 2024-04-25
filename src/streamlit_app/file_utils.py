from pathlib import Path

SCRIPT_PATH = Path(__file__).resolve().parent
UPLOAD_FOLDER = "uploads"  # TODO use pathlib instead
OUTPUT_FOLDER = "outputs"
ALLOWED_PAPER_EXTENSIONS = {".pdf"}
ALLOWED_CONFIG_EXTENSIONS = {".json"}
ERROR_MESSAGE_REJECT_EXTENSION = (
    "{} has wrong extension {}, it will be ignored. see list of allowed formats: {}"
)
upload_folder = SCRIPT_PATH / UPLOAD_FOLDER
output_folder = SCRIPT_PATH / OUTPUT_FOLDER


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
