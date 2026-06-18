<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/cifs-utils/idmapwb.c -->
# sources/user-network-fs/cifs-utils/idmapwb.c

## Purpose

`idmapwb.c` implements `idmapwb.so`, a CIFS ID mapping plugin backed by Samba winbind.

## Important APIs, Types, and Functions

Important functions are `csid_to_wsid`, `wsid_to_csid`, `cifs_idmap_sid_to_str`, `cifs_idmap_str_to_sid`, `wuxid_to_cuxid`, `cifs_idmap_sids_to_ids`, `cifs_idmap_ids_to_sids`, `cifs_idmap_init_plugin`, and `cifs_idmap_exit_plugin`.

## Control Flow

Conversion from CIFS SID to winbind SID copies authority bytes and converts subauthorities from little-endian to host endian. SID-to-string uses `wbcLookupSid` and returns `DOMAIN\name`. String-to-SID accepts either raw SID strings or `DOMAIN\name`/name lookups. SID-to-ID maps arrays through `wbcSidsToUnixIds`; ID-to-SID iterates UID/GID/BOTH inputs and calls winbind UID/GID lookup functions.

## State and Persistence Behavior

The plugin stores only a pointer to the caller's error-message pointer. Persistent mapping state lives in winbind/Samba configuration and databases outside this plugin.

## Dependencies and Integration Points

It depends on libwbclient, endian conversion macros, `cifsidmap.h`, and optional `HAVE_WBC_ID_TYPE_BOTH`. It is built as `idmapwb.so` and loaded through `idmap_plugin.c`.

## Risks and Edge Cases

Winbind availability and configuration determine behavior. Partial array mapping sets unknown types or revision zero markers. The BOTH case prefers UID mapping before GID. String parsing treats names without `\` first as possible raw SID, then as default-domain names.

## Test Signals

Tests should cover SID endian round-trips, raw SID string conversion, domain-name conversion, unknown identities, BOTH behavior, partial array failures, and operation with winbind stopped or returning errors.
<!-- END_FILE_RESEARCH: sources/user-network-fs/cifs-utils/idmapwb.c -->
