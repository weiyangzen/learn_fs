# sources/user-network-fs/samba/source3/libsmb/dsgetdcname.h

## Purpose

This header declares the public domain-controller discovery APIs implemented by `dsgetdcname.c`.

## Important APIs, Types, and Functions

It forward-declares `struct netr_DsRGetDCNameInfo` and `struct messaging_context`, includes talloc and GUID definitions, and declares `dsgetdcname()` plus `dsgetonedcname()`. Both return `NTSTATUS` and allocate the resulting `netr_DsRGetDCNameInfo` under a caller-provided `TALLOC_CTX`.

## Control Flow

The header has no runtime control flow. Callers pass discovery inputs, flags, and a messaging context; the implementation handles cache lookup, DNS/NetBIOS discovery, probing, and result allocation.

## State and Persistence Behavior

The header stores no state. Its API exposes ownership of returned discovery info through talloc and lets the implementation manage gencache/sitename/name-cache state.

## Dependencies and Integration Points

It depends on `replace.h`, `<talloc.h>`, and `librpc/gen_ndr/misc.h` for `struct GUID`. It is included by discovery callers and by `dsgetdcname.c` itself to keep signatures consistent.

## Risks and Test Signals

Risk is mostly API contract drift: callers need a valid messaging context for NetBIOS discovery paths and must provide stable domain/DC strings. Build tests should catch signature drift; runtime tests should verify allocation ownership, null or missing optional GUID/site inputs, and proper status returns for unresolved domains.
