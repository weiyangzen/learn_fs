# sources/storage-engines/badger/.github/workflows/cd-badger.yml

Purpose: manual GitHub Actions release workflow for building and uploading Badger CLI binaries.

Important flow: `workflow_dispatch` requires `releasetag`. Two build jobs check out that ref, set up Go from `go.mod`, validate that the tag starts with `v`, install build dependencies, run `make badger`, generate SHA256 files, tar the platform binary, and upload artifacts. The final `upload-to-release` job downloads artifacts and uses `gh release upload` with `GITHUB_TOKEN`.

State and persistence: persistent outputs are release assets attached to an existing GitHub release. Dependencies include `actions/checkout`, `actions/setup-go`, `actions/upload-artifact`, `actions/download-artifact`, `gh`, `sha256sum`, `tar`, `make`, and platform runners. Risks: release-tag validation only checks prefix, the arm job does not run `apt-get update`, `gh release upload` assumes the release already exists, and `contents: write` is required. Test signals are dry-run workflow dispatch on a test tag, artifact names/checksums, and actionlint.
