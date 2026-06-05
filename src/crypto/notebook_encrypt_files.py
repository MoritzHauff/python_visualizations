import marimo

__generated_with = "0.21.1"
app = marimo.App(width="medium")

with app.setup:
    import json
    import logging
    import marimo as mo
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
    PASSWORD = "STRONG!Password"
    key = get_key(PASSWORD, "src/crypto/test.salt")
    key
    return (key,)


@app.cell
def _(key):
    example_data = {"example": "This is some example data to encrypt."}

    with open("src/crypto/example_data.json", "w") as f:
        json.dump(example_data, f)

    write_encrypted_json("src/crypto/example_data.enc", key, example_data)
    return


@app.cell
def _(key):
    data = read_encrypted_json("src/crypto/example_data.enc", key)
    data
    return


if __name__ == "__main__":
    app.run()
