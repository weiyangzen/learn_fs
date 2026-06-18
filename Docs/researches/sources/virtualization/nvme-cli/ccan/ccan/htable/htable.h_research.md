# File Research: sources/virtualization/nvme-cli/ccan/ccan/htable/htable.h

- Purpose: public raw pointer hash table interface.
- Key structs: `struct htable` and `struct htable_iter`.
- Key APIs: `HTABLE_INITIALIZER`, `htable_init`, `htable_init_sized`, `htable_count`, `htable_clear`, `htable_check`, `htable_copy`, `htable_add`, `htable_del`, `htable_firstval`, `htable_nextval`, `htable_get`, `htable_first`, `htable_next`, `htable_prev`, `htable_delval`, `htable_pick`, and `htable_set_allocator`.
- Debug mode: `CCAN_HTABLE_DEBUG` wraps calls with `htable_check`.
