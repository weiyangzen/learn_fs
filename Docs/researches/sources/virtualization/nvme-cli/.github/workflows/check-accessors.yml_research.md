# File Research: sources/virtualization/nvme-cli/.github/workflows/check-accessors.yml

- Purpose: verifies generated accessor files are in sync with generator output.
- Triggers: push and pull request to `master`, plus manual dispatch.
- Key behavior: runs in the Debian nvme container, configures Meson with `-Dcheck-accessors=true`, then compiles `update-accessors`.
- Policy note: `.h`, `.c`, and `.i` outputs must be byte-identical; `.ld` files are compared at symbol level according to file comments.
