<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/libcli/wbclient/wbclient.c -->
# sources/user-network-fs/samba/source4/libcli/wbclient/wbclient.c

Purpose: adapts Samba internal `id_map` arrays to libwbclient SID/Unix ID conversion APIs.

Important APIs and types: `wbc_sids_to_xids` and `wbc_xids_to_sids`, with `struct id_map`, `struct dom_sid`, `struct unixid`, `struct wbcDomainSid`, and `struct wbcUnixId`. It depends on winbind client environment toggles and libwbclient conversion calls.

Control flow: SID-to-ID allocates temporary arrays, copies internal SIDs into wbc SIDs, temporarily enables winbind if it was disabled by environment, calls `wbcSidsToUnixIds`, restores the previous state, and maps returned ID types back to Samba `ID_TYPE_*`. ID-to-SID validates UID/GID input types, calls `wbcUnixIdsToSids`, duplicates non-null returned SIDs into the caller-owned `ids` array, and marks unmapped null SIDs.

State and persistence: no persistent local state, but winbind process/environment state is toggled around calls. Outputs mutate each `id_map` entry's `xid`, `sid`, and `status`.

Risks: conversion errors collapse to `NT_STATUS_INTERNAL_ERROR`, losing detailed libwbclient diagnostics. In the GID branch, the code initializes `.id.uid` instead of `.id.gid`, which is a suspicious field-selection risk for GID conversions. Test signals include UID, GID, BOTH, NOT_SPECIFIED, unmapped null SID, winbind-off environment restoration, allocation failure, and libwbclient error propagation.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/libcli/wbclient/wbclient.c -->
