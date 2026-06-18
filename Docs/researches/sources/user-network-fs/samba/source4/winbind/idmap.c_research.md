<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/winbind/idmap.c -->
# sources/user-network-fs/samba/source4/winbind/idmap.c

## Purpose

This file implements Samba4 AD DC SID/unixid mapping. It maps Unix UIDs/GIDs to SIDs and SIDs to Unix IDs using RFC2307 attributes in `sam.ldb` when configured, existing mappings in `idmap.ldb`, Unix local SIDs (`S-1-22-*`), and transactional allocation of new idmap entries.

## Important APIs, Types, and Functions

- `idmap_get_bounds()` reads `lowerBound` and `upperBound` from `CN=CONFIG` in `idmap.ldb`.
- `idmap_msg_add_dom_sid()` and `idmap_msg_get_dom_sid()` marshal/unmarshal `dom_sid` values through NDR blobs in LDB messages.
- `idmap_init()` opens `idmap.ldb` and `sam.ldb` with the system session.
- `idmap_xid_to_sid()` maps one `struct unixid` to a SID.
- `idmap_sid_to_xid()` maps one SID to a `struct unixid`, allocating a new idmap entry when needed.
- `idmap_xids_to_sids()` and `idmap_sids_to_xids()` batch arrays of `struct id_map` and set per-entry `ID_MAPPED`/`ID_UNMAPPED`.

## Control Flow

Initialization connects to `idmap.ldb` and `sam.ldb`. UID/GID-to-SID first optionally searches `sam.ldb` for matching `uidNumber`/`gidNumber` when `idmap_ldb:use rfc2307 = true`. If absent, it searches `idmap.ldb` for a compatible `xidNumber` and type. If still absent, local Unix users/groups are represented as calculated `S-1-22-1/2` SIDs without writing an idmap entry.

SID-to-xID first handles local Unix user/group SID namespaces by splitting the RID. It then optionally checks `sam.ldb` RFC2307 attributes. If no existing `sidMap` entry exists in `idmap.ldb`, it starts an LDB transaction, rechecks for races, reads bounds and the high-water mark from `CN=CONFIG`, increments the high-water mark, creates `CN=<sid>` with `objectClass=sidMap`, `objectSid`, `xidNumber`, `type=ID_TYPE_BOTH`, commits, and returns the allocated ID. Batch wrappers retry once on `NT_STATUS_RETRY`.

## State and Persistence Behavior

This file reads persistent `sam.ldb` and reads/writes persistent `idmap.ldb`. New SID-to-xID mappings advance the `xidNumber` high-water mark under `CN=CONFIG` and add a durable `sidMap` record. Transactions protect high-water mark plus mapping creation. Local Unix SID calculations and RFC2307 matches do not write new idmap records.

## Dependencies and Integration Points

Dependencies include LDB, `ldb_wrap_connect`, SAMDB search helpers, NDR SID encoding, LDAP SID encoding, loadparm parameters, Unix SID helpers, DSDB account-type constants, and generated idmap types from `librpc/gen_ndr/idmap.h`. The build exposes this as the `IDMAP` subsystem.

## Risks and Edge Cases

Duplicate RFC2307 matches return `NT_STATUS_NONE_MAPPED`. `idmap_get_bounds()` and allocator correctness depend on a valid `CN=CONFIG`. Allocations return `NT_STATUS_RETRY` if another writer adds the mapping between the initial and transactional lookup. The high-water mark check uses `hwm > high`, so `hwm == high` is still allocated and increments past high. UID/GID-to-SID fallback creates `S-1-22` SIDs without checking whether those UIDs/GIDs exist locally.

## Test Signals

Signals include correct RFC2307 lookup from `sam.ldb`, stable lookup of existing `sidMap` records, transactional allocation of new mappings within bounds, accurate type propagation (`UID`, `GID`, `BOTH`), per-entry batch statuses, `STATUS_SOME_UNMAPPED` for partial failures, and durable idmap entries visible in `idmap.ldb`.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/winbind/idmap.c -->
