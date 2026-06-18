# File Research: sources/virtualization/nvme-cli/ccan/ccan/list/list.h

- Purpose: intrusive doubly linked list implementation.
- Key structs: `struct list_node` and `struct list_head`.
- Key APIs: initialization, add before/after/head/tail, delete, delete-init, delete-from, swap, top/pop/tail, forward/reverse iteration, safe iteration, next/prev, append/prepend whole lists, and offset-based low-level iteration.
- Type safety: uses `container_of`, `check_type`, and offset helpers.
- Debug mode: `CCAN_LIST_DEBUG` enables structural checks and use-after-delete nulling.
