# File Research: sources/virtualization/nvme-cli/libnvme/scripts/kernel-doc-check

This Bash script validates kernel-doc comments without producing docs.

Core behavior:
- Locates sibling `kernel-doc`.
- Runs `kernel-doc -none "$@"`.
- Greps output for `warning` or `error`.
- Exits successfully only when kernel-doc exits 0 and grep finds no warnings/errors.

Integration role:
- CI/developer check wrapper for libnvme API documentation comments.
