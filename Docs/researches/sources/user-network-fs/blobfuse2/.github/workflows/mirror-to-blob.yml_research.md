# sources/user-network-fs/blobfuse2/.github/workflows/mirror-to-blob.yml

## Purpose
This workflow mirrors repository code, wiki content, public documentation, and exported GitHub history into Azure Blob Storage for downstream retrieval or AI/search workflows.

## Important APIs, Types, and Functions
It uses `azure/login@v3`, Azure CLI `az storage copy`, `az storage blob upload-batch`, and `az storage blob download-batch`, plus repository scripts `scripts/fetch_public_docs.py` and `scripts/export_github_history.py`.

## Control Flow
On weekly schedule or manual dispatch, the job authenticates to Azure by OIDC, uploads the repository tree excluding `.git` to `repo-code`, clones and uploads the wiki to `repo-docs/wiki`, fetches public docs and uploads `public/`, restores previous GitHub export state from `repo-gh`, runs the export script with `GITHUB_TOKEN`, and uploads the refreshed JSONL/state output back to `repo-gh`.

## State and Persistence Behavior
Persistent state lives in Azure Blob containers/prefixes `repo-code`, `repo-docs`, and `repo-gh`. The `out_github_export` directory is restored from blob so the exporter can append/update incrementally instead of starting from scratch.

## Dependencies and Integration Points
It depends on Azure OIDC secrets, storage account `blobfusemcpserver`, Azure CLI availability on GitHub-hosted runners, Python `html2text` and `requests`, and public access to the Azure Storage Fuse wiki.

## Risks and Edge Cases
Repository code upload may include files not intended for public AI ingestion unless excluded. The workflow has read permissions for issues and PRs and uploads historical data to blob. Incremental state corruption can affect future exports. `az storage copy` and upload options differ between commands, so destination-path mistakes are easy.

## Test Signals
Signals include blob prefixes updated after a run, restored `state.json` on repeat runs, successful wiki clone, successful script exits, and no unauthorized secret material in uploaded content.
