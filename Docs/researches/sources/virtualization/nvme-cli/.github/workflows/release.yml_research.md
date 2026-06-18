# File Research: sources/virtualization/nvme-cli/.github/workflows/release.yml

- Purpose: creates GitHub releases for version tags.
- Trigger: push to `master` and all tags.
- Guard: job only runs for `refs/tags/v*` in `linux-nvme/nvme-cli`.
- Key behavior: uses `gh release create "${GITHUB_REF_NAME}" --generate-notes` with repository `GITHUB_TOKEN`.
