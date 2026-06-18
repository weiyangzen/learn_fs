# File Research: sources/virtualization/spdk/lib/env_ocf/ocf_env_list.h

Implements a Linux-kernel-like intrusive doubly linked list API for OCF.

Important contents:
- Defines `struct list_head` aligned to 64 bytes.
- Implements `INIT_LIST_HEAD`, `list_add`, `list_add_tail`, `list_empty`, `list_del`, `list_move`, and `list_move_tail`.
- Provides `list_entry`, `list_first_entry`, raw iteration, safe iteration, entry iteration, and safe entry iteration macros.
- Includes poison pointer constants but does not assign them on delete.

Role: lets OCF list-using code build without depending on Linux kernel list headers.
