# sources/user-network-fs/samba/source3/lib/cleanupdb.h

Purpose: declares cleanup database operations for reliable child cleanup tracking.

Important APIs/types/functions: `cleanupdb_store_child(pid, unclean)`, `cleanupdb_delete_child(pid)`, and `cleanupdb_traverse_read(callback, private_data)`.

Control flow: callers record child pids with a cleanup/unclean flag, remove them after normal cleanup, and traverse remaining records to perform recovery.

State and persistence: the header hides the TDB implementation and exposes only pid/bool records through callbacks.

Dependencies/integration: includes `replace.h` for portability and pid/bool types.

Risks/test signals: callback return nonzero stops traversal as an error; callers should not assume ordering. Tests should compile callback signatures and verify boolean semantics match `cleanupdb.c`.
