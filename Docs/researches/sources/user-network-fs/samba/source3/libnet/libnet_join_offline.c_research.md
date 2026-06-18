# sources/user-network-fs/samba/source3/libnet/libnet_join_offline.c

## Purpose

Composes and reads Windows Offline Domain Join provision structures for Samba join flows.

## Important APIs, Types, and Functions

Public functions are `libnet_odj_compose_ODJ_PROVISION_DATA`, `libnet_odj_find_win7blob`, and `libnet_odj_find_joinprov3`. Internal composers build `ODJ_WIN7BLOB`, `OP_JOINPROV3_PART`, `OP_PACKAGE_PART`, `OP_PACKAGE_PART_COLLECTION`, and `OP_PACKAGE`. Provider2 composition is a stub returning `WERR_INVALID_LEVEL`.

## Control Flow

Composition creates two provision blobs: Win7 format with domain, machine, password, SID/GUID, and DC info; and Win8 OP package format with join-provider and provider3 parts. Provider3 stores account RID and full account SID string. Lookup scans provision blobs; Win7 extraction accepts either direct Win7 format or a Win8 package provider part, and provider3 extraction searches the Win8 package for the provider3 GUID.

## State and Persistence Behavior

All state is talloc-owned in-memory generated NDR structures. The implementation does not write files, but generated provision data can be serialized by callers and includes sensitive machine password material.

## Dependencies and Integration Points

Depends on generated ODJ/libnet-join NDR types, SID helpers, and Netlogon DC info. `libnet_join.c` consumes the find helpers during offline join.

## Risks and Test Signals

Risks include clear machine password material in blobs, unimplemented provider2, assumptions about nested package pointers, and strict bad-format handling. Tests should round-trip composed data, verify Win7/provider3 extraction, cover malformed wrapped collections, trailing `$` machine names, invalid GUID levels, and offline join consumption.
