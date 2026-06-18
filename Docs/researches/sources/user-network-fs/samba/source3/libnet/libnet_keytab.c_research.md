# sources/user-network-fs/samba/source3/libnet/libnet_keytab.c

## Purpose

Provides Kerberos keytab management helpers for libnet. It opens a writable keytab, stages entries, removes duplicates or stale entries, derives keys, adds entries, and searches existing keytab content.

## Important APIs, Types, and Functions

Public functions are `libnet_keytab_init`, `libnet_keytab_add`, `libnet_keytab_search`, and `libnet_keytab_add_to_keytab_entries`. Internal helpers are `keytab_close`, `libnet_keytab_remove_entries`, and `libnet_keytab_add_entry`.

## Control Flow

Initialization creates a Kerberos context, opens a relative keytab with write access, records the resolved name, and installs a talloc destructor. Callers stage entries as `prefix/name@realm`. `libnet_keytab_add` optionally removes old matching principal/enctype entries, then removes exact duplicates and adds each entry. Adding parses the principal, fetches Samba's salt principal from secrets, derives a key with `create_kerberos_key_from_string`, and writes it. Search iterates the keytab for exact principal, kvno, and enctype and returns copied key bytes.

## State and Persistence Behavior

`libnet_keytab_context` stores Kerberos handles, keytab name, ADS pointer, realm, staged entries, and cleanup flag. Persistent effects are mutations to the keytab. Code is compiled only under `HAVE_KRB5`.

## Dependencies and Integration Points

Depends on Samba Kerberos wrappers, ADS/secrets helpers, talloc arrays, and types from `libnet_keytab.h`. Used by DSSync keytab import and join keytab paths.

## Risks and Test Signals

Risks include key derivation semantics when caller data may already be key material, reliance on secrets salt principal, restart-heavy keytab removal, exact kvno search behavior, and sensitive bytes in memory. Tests should cover init failures, duplicate replacement, clean-old behavior, search hits/misses, multi-enctype entries, and non-Kerberos builds.
