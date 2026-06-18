# sources/user-network-fs/samba/source3/winbindd/winbindd_allocate_gid.c

Purpose: async implementation of privileged `WINBINDD_ALLOCATE_GID`, allocating a new Unix GID through the idmap child.

Important APIs and types: `winbindd_allocate_gid_send/recv`; `struct winbindd_allocate_gid_state` with event context and `uint64_t gid`.

Control flow: `send` creates state, logs the request, and starts `wb_parent_idmap_setup_send`. The setup callback validates idmap config and fails with `NT_STATUS_UNSUCCESSFUL` if no idmap domains are configured, matching idmap_tdb range-full behavior. It then calls `dcerpc_wbint_AllocateGid_send` on `idmap_child_handle`. The final callback merges transport/result status and completes. `recv` writes `response->data.gid`.

State and persistence: allocation persistence is owned by the idmap backend/child, not this wrapper. This file only holds the allocated value in request state.

Dependencies and integration points: parent idmap setup, idmap child RPC, privileged command dispatch in `winbindd.c`, and `winbindd_response` protocol fields.

Risks: no local validation of caller privilege; depends on dispatch table placement. No configured idmap domain and exhausted range both surface as unsuccessful. Returned `uint64_t` is assigned to protocol response field, so type/range compatibility matters.

Test signals: privileged command success, no idmap config, range exhaustion/backend failure, idmap child transport failure, and response field correctness.
