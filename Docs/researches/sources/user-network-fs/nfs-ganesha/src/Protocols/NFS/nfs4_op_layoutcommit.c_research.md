# sources/user-network-fs/nfs-ganesha/src/Protocols/NFS/nfs4_op_layoutcommit.c

Purpose: implements pNFS `LAYOUTCOMMIT`, committing client layout writes and optional size/mtime updates back through the FSAL.

Important APIs and types: uses `LAYOUTCOMMIT4args`, `LAYOUTCOMMIT4res`, `LAYOUTCOMMIT4resok`, `state_t`, `state_layout_segment_t`, `fsal_layoutcommit_arg`, `fsal_layoutcommit_res`, and XDR decode streams. It calls `nfs4_sanity_check_FH`, `nfs4_Check_Stateid`, `obj_ops->layoutcommit`, and state ref helpers.

Control flow: minorversion 0 and non-regular current FHs are rejected. The handler maps optional `loca_last_write_offset` and `loca_time_modify` fields into FSAL args, creates an XDR decode stream over `loca_layoutupdate.lou_body`, and validates the supplied layout stateid. It sets the FSAL layout type from the layout state, locks the current object's state, and iterates all layout segments attached to the state. For each segment it passes segment metadata and FSAL segment data to `layoutcommit`. If the FSAL says `commit_done`, iteration stops; otherwise the XDR stream is reset to the original body start for the next segment. The response reports new size only if the FSAL supplied one.

State and persistence: does not directly modify SAL layout lists, but commits data/metadata to the backing FSAL and may cause persistent file size or mtime updates via FSAL implementation. Holds state lock while iterating segments.

Dependencies and integration: integrated with layout state validation, pNFS FSAL layoutcommit callbacks, XDR layout-specific opaque decoding, and NFSv4.1 status mapping.

Risks: every segment reuses the same opaque body; FSAL implementations must tolerate reset decode streams. Holding state lock across FSAL callbacks can be expensive or deadlock-prone if FSAL re-enters state. Error paths must release layout state and destroy the XDR stream.

Test signals: minorversion 0, invalid FH, bad layout stateid, multiple segments with `commit_done` false/true, layout body decode failure in FSAL, size-supplied response, and state/XDR cleanup on errors.
