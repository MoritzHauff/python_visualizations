# Publish marimo notebooks to GitHub Pages

https://docs.marimo.io/guides/publishing/github/#publish-to-github-pages

## Export to WASM-powered HTML

Export your notebook to a self-contained HTML file that runs using [WebAssembly](https://docs.marimo.io/guides/wasm/):

```sh
marimo export html-wasm notebook.py -o output_dir --mode edit
```
```
```

## Publish using GitHub Actions

Either fork the marimo [template repository](https://github.com/marimo-team/marimo-gh-pages-template) for deploying multiple notebooks to Github Pages.

Or add the following GitHub Actions workflow, which will republish your notebook on git push.

```
jobs:
    build:
        runs-on: ubuntu-latest

        steps:
            # ... checkout and install dependencies

            - name: 📄 Export notebook
              run: |
                  marimo export html-wasm notebook.py -o path/to/output --mode run

            - name: 📦 Upload Pages Artifact
              uses: actions/upload-pages-artifact@v3
              with:
                  path: path/to/output

    deploy:
        needs: build
        runs-on: ubuntu-latest
        environment:
            name: github-pages
            url: ${{ steps.deployment.outputs.page_url }}

        permissions:
            pages: write
            id-token: write

        steps:
            - name: 🌐 Deploy to GitHub Pages
              id: deployment
              uses: actions/deploy-pages@v4
              with:
                  artifact_name: github-pages
```
```

```
