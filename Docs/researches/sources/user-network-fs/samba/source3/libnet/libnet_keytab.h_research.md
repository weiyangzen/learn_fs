# sources/user-network-fs/samba/source3/libnet/libnet_keytab.h

## Purpose

Declares libnet keytab context, entry structures, and helper APIs when Samba is built with Kerberos.

## Important APIs, Types, and Functions

Under `HAVE_KRB5`, `struct libnet_keytab_entry` stores name, principal, password/key blob, kvno, and enctype. `struct libnet_keytab_context` stores Kerberos context/keytab handles, keytab name, ADS pointer, DNS realm, staged entries, and cleanup flag. Declared APIs are initialization, add, search, and staged-entry append.

## Control Flow

Users initialize a context, set realm and cleanup behavior, stage entries, then commit them with `libnet_keytab_add`. `libnet_keytab_search` lets consumers recover existing real or synthetic entries.

## State and Persistence Behavior

Defines in-memory staging for persistent keytab writes. `DATA_BLOB password` can hold plaintext-like material, raw key material, or serialized state by caller convention.

## Dependencies and Integration Points

Depends on Kerberos types, Samba `DATA_BLOB`, and `struct ads_struct`. Included by keytab utilities, DSSync keytab backend, and join-related code.

## Risks and Test Signals

Risks include APIs being unavailable in non-Kerberos builds, ambiguous password/key semantics, and required realm setup before principal construction. Tests should compile with and without `HAVE_KRB5` and exercise add/search through the implementation.
