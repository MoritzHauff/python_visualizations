# Publish marimo notebooks to GitHub Pages


## Prepare notebook for WASM

https://docs.marimo.io/guides/wasm/#packages

When developing notebooks locally that you plan to share as WASM notebooks, create them with
`marimo edit --sandbox notebook.py`. This inlines your package dependencies into the notebook file,
ensuring they are seamlessly installed in our WebAssembly environment.
See [package management](https://docs.marimo.io/guides/editor_features/package_management/) for more details.

## Export to WASM-powered HTML

https://docs.marimo.io/guides/publishing/github/#publish-to-github-pages

Export your notebook to a self-contained HTML file that runs using [WebAssembly](https://docs.marimo.io/guides/wasm/):
```sh
marimo export html-wasm notebook.py -o output_dir --mode edit
```

or for read-only:
```sh
marimo export html-wasm notebook.py -o output_dir --mode run
```

## Publish using GitHub Actions

### Multiple notebooks

> [!IMPORTANT]
> TODO
> Either fork the marimo [template repository](https://github.com/marimo-team/marimo-gh-pages-template) for deploying multiple notebooks to Github Pages.

### Single notebooks workflow
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

### Single notebooks manually

You can also publish an exported notebook manually through your repository settings. Read [GitHub's documentation](https://docs.github.com/en/pages/getting-started-with-github-pages/configuring-a-publishing-source-for-your-github-pages-site) to learn more.

Make sure to [include a `.nojekyll` file](https://github.blog/news-insights/bypassing-jekyll-on-github-pages/) in root folder from which your site is built to prevent GitHub from interfering with your site.

