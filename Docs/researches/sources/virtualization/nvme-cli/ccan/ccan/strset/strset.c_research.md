# File Research: sources/virtualization/nvme-cli/ccan/ccan/strset/strset.c

- Purpose: crit-bit string set implementation.
- Key APIs implemented: `strset_get`, `strset_add`, `strset_del`, `strset_iterate_`, `strset_prefix`, and `strset_clear`.
- Storage policy: stores caller-provided string pointers; it does not duplicate strings.
- Special cases: uses a special empty-string node because strings and internal nodes are distinguished by leading zero byte.
- Error policy: sets `errno` to `ENOENT`, `EEXIST`, or `ENOMEM` for common failure cases.
