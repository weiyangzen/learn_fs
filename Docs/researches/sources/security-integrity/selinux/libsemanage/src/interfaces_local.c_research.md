# sources/security-integrity/selinux/libsemanage/src/interfaces_local.c

Purpose: local network-interface CRUD wrappers over the handle's local interface database.

Important APIs: `semanage_iface_modify_local`, `del_local`, `query_local`, `exists_local`, `count_local`, `iterate_local`, and `list_local`.

Control flow: every function selects `semanage_iface_dbase_local(handle)` and delegates to the corresponding `dbase_*` routine. No local duplicate or context validation is performed in this file.

State/persistence: modifies or reads local interface records that are later flushed by commit component logic. Dependencies are `iface_internal.h`, `handle.h`, and `database.h`.

Risks: correctness relies on generic database key uniqueness and parser/context checks elsewhere. Test signals include write/restore cycles in wrapper tests, local query/list/count, and commit flush of interface changes.
