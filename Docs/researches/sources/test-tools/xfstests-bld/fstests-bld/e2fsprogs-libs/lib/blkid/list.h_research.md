# sources/test-tools/xfstests-bld/fstests-bld/e2fsprogs-libs/lib/blkid/list.h

Purpose: provides a small Linux-kernel-style intrusive doubly linked list implementation for libblkid internals.

Important APIs/types/functions: `struct list_head` stores `next`/`prev`. Macros/functions include `LIST_HEAD_INIT`, `LIST_HEAD`, `INIT_LIST_HEAD`, `__list_add`, `list_add`, `list_add_tail`, `__list_del`, `list_del`, `list_del_init`, `list_empty`, `list_splice`, `list_entry`, `list_for_each`, and `list_for_each_safe`.

State and persistence: no global state. List membership is embedded in owning structs such as devices and tags.

Dependencies and integration: included by `blkidP.h`; guarded to avoid conflict if a system `LIST_HEAD` already exists. Supports C++ linkage wrappers.

Risks and test signals: no runtime validation, type safety, or poisoning after delete; misuse can corrupt cache graphs. Test add/delete/splice ordering, safe iteration while freeing, empty-list behavior, and `list_entry` offsets on supported compilers.
