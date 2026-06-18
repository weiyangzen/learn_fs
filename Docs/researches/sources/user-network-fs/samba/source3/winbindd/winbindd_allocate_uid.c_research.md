# sources/user-network-fs/samba/source3/winbindd/winbindd_allocate_uid.c

Purpose: async implementation of privileged `WINBINDD_ALLOCATE_UID`, allocating a new Unix UID through the idmap child.

Important APIs and types: `winbindd_allocate_uid_send/recv`; `struct winbindd_allocate_uid_state` with event context and `uint64_t uid`.

Control flow: `send` creates state, logs the request, and starts `wb_parent_idmap_setup_send`. The setup callback validates idmap config and fails with `NT_STATUS_UNSUCCESSFUL` when no domains are configured. It calls `dcerpc_wbint_AllocateUid_send` on `idmap_child_handle`. The final callback merges RPC transport/result status and completes. `recv` writes `response->data.uid`.

State and persistence: actual UID allocation is persisted by the idmap backend behind the child RPC. The wrapper stores only transient request state.

Dependencies and integration points: parent idmap config, idmap child RPC, privileged async dispatch in `winbindd.c`, and winbind client response protocol.

Risks: privilege depends on command dispatch, not this file. No-domain and exhausted-range failures intentionally share status. Returned value width must match response consumers. Allocation semantics depend entirely on idmap backend atomicity.

Test signals: successful privileged allocation, missing idmap config, backend/range exhaustion, child RPC failure, response field population, and denial when invoked over the nonprivileged socket.
