# File Research: sources/virtualization/nvme-cli/ccan/ccan/list/list.c

- Purpose: runtime consistency checks for CCAN intrusive lists.
- Key APIs: `list_check_node` and `list_check`.
- Behavior: traverses forward links and validates each node’s `prev`; reports corruption to stderr and aborts when an abort string is provided.
- Used by: `list.h` debug wrappers under `CCAN_LIST_DEBUG`.
