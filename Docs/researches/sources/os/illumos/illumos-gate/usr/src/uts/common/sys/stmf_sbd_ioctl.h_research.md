# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/stmf_sbd_ioctl.h

## Role

Ioctl ABI for the STMF SBD logical-unit provider, covering creation, import, deletion, modification, property lookup, LU listing, standby/global LU controls, and unmap properties.

## Key Contents

Defines provider-specific return codes for metadata creation, block size, separate metadata requirements, duplicate file/GUID, invalid paths, lookup/open/getattr failures, type mismatch, file size/alignment/range/support errors, missing metadata, version unsupported, busy/not found, insufficient buffer, write-cache failure, and access-state failure.

Defines SBD ioctl numbers and payload structures: `sbd_create_and_reg_lu_t`, `sbd_global_props_t`, `sbd_set_lu_standby_t`, `sbd_import_lu_t`, `sbd_modify_lu_t`, `sbd_delete_lu_t`, `sbd_lu_props_t`, and `sbd_unmap_props_t`.

## Design Notes

Most request structures include structure size, validity bitfields, offset fields into trailing buffers, fixed VPD strings, GUIDs, and “likely more than 8” trailing arrays. The ABI is designed for variable-length path, alias, URL, and serial data while keeping the fixed header stable.
