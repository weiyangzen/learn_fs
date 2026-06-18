# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/isave.h

Declares the interpreter save/restore interface. It explains why save objects are represented by unique numeric save IDs rather than direct `t_struct` references: this avoids requiring all save objects to live in global VM and avoids special invalidation after restore.

Exports initialization, save lookup, save creation, current save lookup, pointer/name recency checks, restore stepping, save forgetting, and full VM release. It also exposes internal state toggles `alloc_set_in_save` and `alloc_set_not_in_save`, plus hooks used by restore logic such as `font_restore`, `restore_check_save`, and `dorestore`.

This header is the public contract for `isave.c` and expects interpreter memory types from `imemory.h` and `idosave.h`.
