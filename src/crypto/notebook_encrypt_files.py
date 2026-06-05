import marimo

__generated_with = "0.21.1"
app = marimo.App(width="medium")

with app.setup:
    import json
    import logging
    import marimo as mo
    from pathlib import Path
    from crypto.encryption import get_key, write_encrypted_json, read_encrypted_json

    #logging.basicConfig(level=logging.DEBUG)
    #import logging
    #import sys
    #
    #logger = logging.getLogger("myapp")
    #logger.setLevel(logging.DEBUG)
    #
    #handler = logging.StreamHandler(sys.stdout)
    #handler.setFormatter(logging.Formatter("%(levelname)s - %(message)s"))
    #
    ## Avoid duplicate logs if re-running the cell
    #if not logger.handlers:
    #    logger.addHandler(handler)


@app.cell
def _():
    ui_path_file = mo.ui.text(label="Enter the path to the encrypted file:", placeholder="src/crypto/example_data.enc")
    ui_text_password = mo.ui.text(label="Enter the password:", placeholder="Your password", kind="password")
    ui_run_button_save = mo.ui.run_button(label="Save Encrypted Data")
    return ui_path_file, ui_run_button_save, ui_text_password


@app.cell
def _(ui_path_file, ui_run_button_save, ui_text_password):
    mo.vstack([ui_path_file, ui_text_password, ui_run_button_save])
    return


@app.cell
def _(ui_path_file, ui_run_button_save, ui_text_password):
    path = None
    if ui_run_button_save.value:
        path = Path(ui_path_file.value)
        print(path)
        if not path:
            raise ValueError("Please enter a valid file path.")
        password = ui_text_password.value
        key = get_key(password, path.with_suffix(".salt"))

        data = prepare_data()
        write_encrypted_json(path.with_suffix(".enc"), key, data)

        # Save data as plain text for debugging
        with open(path.with_suffix(".json"), "w") as f:
            json.dump(data, f)
    return key, path


@app.function
def prepare_data():
    example_data = {
        "name": "Alice",
        "age": 30,
    }
    return example_data


@app.cell
def _(key, path):
    _data = None
    if path:
        _data = read_encrypted_json(path.with_suffix(".enc"), key)
    _data
    return


if __name__ == "__main__":
    app.run()
