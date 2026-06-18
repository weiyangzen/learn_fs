# sources/user-network-fs/nfs-ganesha/src/Protocols/NFS/nfs4_op_layoutreturn.c

Purpose: implements pNFS `LAYOUTRETURN` plus shared layout return helpers used by `LAYOUTGET` cleanup and recalls.

Important APIs and types: exports `nfs4_op_layoutreturn`, `handle_recalls`, and `nfs4_return_one_state`. Uses `LAYOUTRETURN4args/res`, `layoutreturn_file4`, `layoutreturn_stateid`, `state_t`, `state_owner_t`, `state_layout_segment_t`, `state_layout_recall_file`, `fsal_layoutreturn_arg`, `pnfs_segment`, and XDR decode streams.

Control flow: the top-level operation rejects v4.0, then dispatches by return type. `LAYOUTRETURN4_FILE` validates the current regular file, optionally resolves the layout stateid under state lock, builds the requested segment, calls `nfs4_return_one_state`, and either invalidates current stateid if the state was deleted or updates and returns a new stateid. `LAYOUTRETURN4_FSID` records the current fsid and falls through to the ALL-style loop. FSID/ALL returns initialize a temporary root op context, iterate the clientid owner's state list while carefully dropping `so_mutex` around work, set the correct export context per state, lock each object's state, and return matching layout states. `handle_recalls` removes satisfied recall entries and returns recall cookies. `nfs4_return_one_state` iterates layout segments, calls FSAL `layoutreturn` for contained or overlapping segments, deletes or shrinks segments, and deletes the layout state when no segments remain; reclaim returns call FSAL without recorded segments.

State and persistence: mutates layout segment lists, recall lists, layout stateids, current stateid validity, and possibly deletes layout states. It may switch `op_ctx` export context for bulk returns. No stable storage is directly updated.

Dependencies and integration: used by layoutget forgetful-state handling, recall completion, FSAL pNFS return callbacks, SAL state lists, export references, and NFSv4.1 clientid owner state tracking.

Risks: the FSID branch compares `fsid` to `data->current_obj->fsid` while iterating different `obj` values, which is suspicious and should be tested. `alloca(sizeof(arg)+sizeof(void *)*(recalls-1))` is risky when `recalls` is zero because of unsigned underflow. Bulk iteration restarts are necessary but easy to break. FSAL calls under state lock may be costly.

Test signals: file return with full deletion, partial segment shrink, reclaim return, recall cookie satisfaction, FSID return across multiple states, ALL return restart behavior, stale state refs, and zero-recall layoutreturn path.
