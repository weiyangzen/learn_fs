# sources/user-network-fs/nfs-ganesha/src/support/nfs_filehandle_mgmt.c

## Purpose
This file converts between FSAL object handles and NFSv3/NFSv4 wire filehandles, validates Ganesha filehandle structure, resolves NFSv3 handles back to FSAL objects, and performs NFSv4 compound current/saved filehandle sanity checks.

## Important APIs, Types, And Functions
Important functions include `nfs3_FhandleToCache` under NFSv3, `nfs4_FSALToFhandle`, `nfs3_FSALToFhandle`, `nfs4_Is_Fh_DSHandle`, `nfs4_Is_Fh_Invalid`, `nfs3_Is_Fh_Invalid`, `nfs4_sanity_check_FH`, and `nfs4_sanity_check_saved_FH`. The implementation manipulates `file_handle_v3_t`, `file_handle_v4_t`, `nfs_fh3`, `nfs_fh4`, `gsh_buffdesc`, `fsal_export`, and `fsal_obj_handle`.

## Control Flow
Outbound conversion allocates or clears the protocol filehandle buffer, points a descriptor at the embedded `fsopaque` area, asks the FSAL object to encode itself with `handle_to_wire`, fills Ganesha version, endian flags, FSAL opaque length, and export id, then sets the final protocol length. Inbound v3 conversion validates the handle, asserts the export id matches the current export, calls export `wire_to_host`, then `create_handle`. Sanity checks validate empty/invalid handles, required object type, and whether pNFS data-server handles are allowed for the operation.

## State And Persistence
The file has no global mutable state. It serializes export id, version, endian flags, and FSAL opaque bytes into wire handles that may persist on clients and return in later requests. That makes handle layout and version compatibility externally visible.

## Dependencies And Integration Points
It depends on NFS protocol headers, FSAL conversion operations, export manager state in `op_ctx`, filehandle layout helpers/macros, logging, and `nfs_convert` for status conversion. It is central to LOOKUP/GETFH/PUTFH style protocol flows.

## Risks And Test Signals
Risks include fixed maximum assumptions for host handles, assert-only export-id checking in v3 inbound conversion, endian flag compatibility, VMware short-handle warning behavior, and precise status mapping for wrong object types. Tests should round-trip FSAL handles through v3/v4 encoders and decoders, validate malformed length/version/fs_len cases, exercise DS-handle rejection, required-type errors for directory/symlink/non-directory operations, and FSAL `handle_to_wire`/`wire_to_host` failures.
