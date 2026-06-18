# File Research: sources/virtualization/nvme-cli/ccan/ccan/strset/strset.h

- Purpose: public API for the crit-bit string set.
- Key struct: `struct strset`, exposing a union of node pointer or string pointer for embedding/inlining.
- Key APIs: `strset_init`, `strset_empty`, `strset_get`, `strset_add`, `strset_del`, `strset_clear`, `strset_iterate`, `strset_iterate_`, and `strset_prefix`.
- Type safety: `strset_iterate` uses `typesafe_cb_preargs` to validate callback argument type.
