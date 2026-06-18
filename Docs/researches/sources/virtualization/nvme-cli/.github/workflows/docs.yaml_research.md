# File Research: sources/virtualization/nvme-cli/.github/workflows/docs.yaml

- Purpose: documentation build CI.
- Triggers: push and pull request to `master` only when `Documentation/**` or `libnvme/doc/**` changes, plus manual dispatch.
- Key behavior: runs in Debian container and executes `scripts/build.sh docs`.
- Scope: validates nvme-cli and libnvme documentation generation paths.
