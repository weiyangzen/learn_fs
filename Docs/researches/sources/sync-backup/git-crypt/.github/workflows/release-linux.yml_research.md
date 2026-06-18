# sources/sync-backup/git-crypt/.github/workflows/release-linux.yml

Purpose: GitHub Actions workflow that builds and uploads a Linux x86_64 git-crypt release binary when a release is published.

Important APIs/types/functions: same two-job structure as the ARM64 workflow, using `ubuntu-22.04` for build and `ubuntu-latest` for upload, with `actions/checkout@v3`, `actions/upload-artifact@v4`, `actions/download-artifact@v4`, and `actions/github-script@v6`.

Control flow: checkout, install `libssl-dev`, run `make`, upload `git-crypt` artifact, then download and upload it to the release as `git-crypt-${release.name}-linux-x86_64`.

State/persistence behavior: the binary moves through the Actions artifact store and becomes a release asset. Permissions are narrowed to `contents: read` for build and `contents: write` for upload.

Dependencies/integration: relies on Ubuntu package OpenSSL headers/libraries, the C++ Makefile, and release event metadata.

Risks/test signals: no checksum, signature, or architecture validation is performed. Release tests should verify the output is executable, linked as expected, built from the intended tag, and asset upload does not collide with existing assets.
