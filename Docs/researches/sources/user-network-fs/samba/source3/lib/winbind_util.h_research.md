# sources/user-network-fs/samba/source3/lib/winbind_util.h

## Purpose
This header declares the source3 winbind utility wrapper API.

## Important APIs and Types
It exposes name/SID lookup, SID/id mapping, winbind ping, trust-domain check, RID batch lookup, id allocation, and user SID expansion functions. It includes LSA and idmap generated headers plus libwbclient for `wbcErr`.

## Dependencies and Integration Points
The header is the integration contract between source3 identity consumers and `winbind_util.c`. It intentionally exposes Samba types (`dom_sid`, `unixid`, `lsa_SidType`) rather than raw libwbclient structures.

## Risks and Test Signals
Compile-time risk is header include ordering because it references generated NDR and libwbclient types. ABI tests should ensure signatures match both winbind-enabled and stub implementations.
