# sources/user-network-fs/samba/source3/rpc_server/fss/srv_fss_private.h

Purpose: private data model and persistence API for the File Server Remote VSS Protocol server.

Important APIs/types/functions: defines `FSS_DB_NAME`, `struct fss_sc_smap`, `struct fss_sc`, `enum fss_sc_state`, `struct fss_sc_set`, `struct fss_global`, `fss_state_store`, and `fss_state_retrieve`.

Control flow: the structures encode the parent-child hierarchy used by `srv_fss_agent.c`: a global context owns shadow copy sets; each set owns shadow copies; each shadow copy owns share mappings. The state enum models the protocol lifecycle from started to recovered.

State/persistence behavior: `FSS_DB_NAME` is `srv_fss.tdb`. Stored state includes set IDs/state/context/counts, snapshot IDs/base volumes/snapshot paths/timestamps, and mapping names/comments/exposure flags. `fss_global` also tracks the current requested context and the sequence timer, which are runtime-only.

Dependencies/integration: depends on Samba GUID, talloc, tevent timer, NTSTATUS, and list-link conventions used by `DLIST_*` macros in the implementation.

Risks/test signals: count fields must remain synchronized with linked lists because retrieval validates expected child counts. The misspelled `FSS_SC_COMMITED` enumerator is part of the local API and must remain consistent across generated state serialization and agent logic. Tests should cover ABI/compile compatibility and persistence round trips for all state values.
