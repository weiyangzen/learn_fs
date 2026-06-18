# sources/user-network-fs/samba/source3/libads/cldap.h

## Purpose
This header declares the libads CLDAP netlogon v5 helper.

## Important APIs and Types
It includes netlogon definitions and declares `ads_cldap_netlogon_5`, which takes a memory context, target socket address, realm, required flags, and output `NETLOGON_SAM_LOGON_RESPONSE_EX`.

## Dependencies and Integration Points
It is paired with `cldap.c` and consumed by AD discovery code that needs a compact CLDAP ping API.

## Risks and Test Signals
Compile coverage should verify generated netlogon types are visible. Runtime ownership expectations for strings inside the copied reply should be tested by callers.
