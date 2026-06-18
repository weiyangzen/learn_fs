# sources/user-network-fs/samba/source3/lib/winbind_util.c

## Purpose
`winbind_util.c` wraps libwbclient identity mapping and lookup operations behind source3-friendly functions, with stubbed no-winbind implementations when Samba is built without winbind.

## Important APIs and Functions
With `WITH_WINBIND`, exports include passwd lookups (`winbind_getpwnam`, `winbind_getpwsid`), name/SID translation (`winbind_lookup_name`, `winbind_lookup_name_ex`, `winbind_lookup_sid`), daemon health (`winbind_ping`), SID/id mapping (`winbind_sid_to_uid`, `winbind_sid_to_gid`, `winbind_xid_to_sid`), trust check (`wb_is_trusted_domain`), batch RID lookup (`winbind_lookup_rids`), id allocation, and user SID expansion (`winbind_lookup_usersids`). The `#else` branch returns false, null, or benign unknown results.

## Control Flow and State
The functions convert between Samba `dom_sid`/`unixid`/`lsa_SidType` and libwbclient structures, call `wbc*` APIs, copy results to talloc memory where needed, and free libwbclient-allocated memory. `winbind_lookup_name_ex` maps libwbclient errors to NTSTATUS and treats `SERVER_DISABLED` as `NONE_MAPPED` outside domain security.

## Dependencies and Integration Points
It depends on `nsswitch/libwbclient/wbclient.h`, SID structures, idmap NDR types, `tcopy_passwd`, loadparm security mode, and NTSTATUS mapping from `wbcErr`. It integrates with authentication, authorization, idmap, and account lookup code that should not call libwbclient directly.

## Risks and Test Signals
Memory ownership is mixed: libwbclient allocations must be freed with `wbcFreeMemory`, while returned Samba data is talloc-owned. `winbind_lookup_rids` does not explicitly check every talloc allocation after the three top-level arrays, so low-memory tests are useful. The stubs intentionally report unavailable services; callers must distinguish unsupported from not found. Tests should cover enabled and disabled builds, error mapping in `winbind_lookup_name_ex`, SID/id conversions, batch RID ownership, and no-winbind fallbacks.
