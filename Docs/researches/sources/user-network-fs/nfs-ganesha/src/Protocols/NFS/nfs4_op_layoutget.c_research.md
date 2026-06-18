# sources/user-network-fs/nfs-ganesha/src/Protocols/NFS/nfs4_op_layoutget.c

Purpose: implements pNFS `LAYOUTGET` and also contains simple handlers for NFSv4.2 `LAYOUTERROR` and `LAYOUTSTATS`.

Important APIs and types: key helpers are `acquire_layout_state`, `free_layouts`, `one_segment`, `nfs4_op_layoutget`, `nfs4_op_layouterror`, and `nfs4_op_layoutstats`. It uses `state_t`, `state_owner_t`, `state_refer`, `fsal_layoutget_arg/res`, `layout4`, `state_layout_segment_t`, pNFS segment helpers, and XDR encode streams.

Control flow: `acquire_layout_state` validates the supplied stateid under the state lock. Existing layout stateids are reused; share, deleg, or lock stateids create a per-clientid layout state after returning and deleting any prior layout state of the same type, supporting forgetful clients. `one_segment` allocates a layout body buffer sized by `fs_loc_body_size`, asks the FSAL `layoutget` to encode one segment, records the returned segment in SAL via `state_add_segment`, and frees on failure. `nfs4_op_layoutget` rejects v4.0 and non-regular FHs, verifies pNFS support via `fs_maximum_segments`, acquires layout state, then repeatedly grants segments until `last_segment`. It tracks response size and remaining maxcount, checks response room, updates the layout stateid under lock, and returns the layout array. Failure frees partial layouts, deletes brand-new zero-seqid layout state, and invalidates current stateid. `LAYOUTERROR` and `LAYOUTSTATS` currently log client reports and return OK without persistence.

State and persistence: creates and updates layout stateids, stores FSAL segment data on state segment lists, increments a `granting` counter while FSAL layoutget is active, and can return/delete forgotten layouts. No stable storage is touched.

Dependencies and integration: relies on SAL state locking and refs, pNFS FSAL `layoutget`, FSAL max segment and body sizing, `nfs4_return_one_state` from layoutreturn code, compound response sizing, and NFSv4.1 session slot references.

Risks: failure cleanup around partially added segments is delicate; a segment may be in SAL even if later response-size checking fails. The function holds object state locks across FSAL layoutget and state updates. `arg.maxcount` subtraction can underflow if a segment exceeds remaining maxcount. Layout stats/error handlers are currently observability only.

Test signals: v4.0 rejection, unsupported pNFS, new layout state from share state, reuse existing layout state, forgetful-client deletion path, multi-segment layout, response-room failure after segments, FSAL error cleanup, and layoutstats/layouterror logging behavior.
