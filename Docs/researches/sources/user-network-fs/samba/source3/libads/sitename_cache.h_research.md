# sources/user-network-fs/samba/source3/libads/sitename_cache.h

## Purpose

`sitename_cache.h` declares the small ADS client site-name cache API used by DC discovery.

## Important APIs, Types, and Functions

The header exports `sitename_store`, `sitename_fetch`, and `stored_sitename_changed`.

## Control Flow

Callers store site names after CLDAP replies, fetch them before site-specific DNS lookup, and compare candidate values when deciding whether cached site state changed.

## State and Persistence Behavior

The header itself has no state; the implementation stores values in Samba gencache. `sitename_fetch` returns a caller-owned talloc string.

## Dependencies and Integration Points

It relies on declarations from the common Samba include environment for `bool` and `TALLOC_CTX`. It is included by `ldap.c` and implemented by `sitename_cache.c`.

## Risks and Test Signals

Risks are ownership misunderstandings for fetched strings and broad inclusion without explicit includes. Compile tests should include the header from normal ADS callers, and runtime tests should validate store/fetch/change behavior through the implementation.
