# sources/user-network-fs/samba/source4/kdc/hdb-samba4-plugin.c

## Purpose
`hdb-samba4-plugin.c` registers the Heimdal HDB method named `samba4`. It exists primarily for HDB-backed keytab access, especially `HDBGET:samba4:&<base_ctx_pointer>` style lookups used by the kpasswd integration.

## Important APIs, Types, And Functions
`hdb_samba4_create` parses an argument string of the form `&%p`, treats the pointer as a `struct samba_kdc_base_context`, and calls `hdb_samba4_kpasswd_create_kdc`. `hdb_samba4_init` and `hdb_samba4_fini` are no-op method lifecycle hooks for newer HDB interfaces. The exported `struct hdb_method hdb_samba4_interface` sets `prefix = "samba4"` and points `.create` at the creator.

## Control Flow
Heimdal calls the method create hook when a `samba4` HDB/keytab name is opened. The create hook validates the pointer syntax, recovers the talloced base context, builds a restricted kpasswd HDB using Samba's normal KDC DB setup, and maps Samba `NTSTATUS` setup failures to `EINVAL` with Kerberos error messages.

## State And Persistence Behavior
This file owns no persistent state. It bridges a process-local pointer from a keytab name into an HDB object that subsequently opens `sam.ldb` through `hdb_samba4_kpasswd_create_kdc`.

## Dependencies And Integration Points
It depends on `kdc/kdc-glue.h`, Samba loadparm helpers for private paths, and Heimdal's HDB method ABI. The compile-time `HDB_INTERFACE_VERSION` check enforces version 12.

## Risks
The pointer-in-string design is intentionally described as an ugly private hook. It is process-local and must never be treated as externally trusted input. A mismatch between build-time and runtime HDB ABI would break keytab/kpasswd service creation, and incompatible DSDB versions are surfaced as `EINVAL`.

## Test Signals
Signals include kpasswd startup, `HDBGET:samba4:&...` keytab lookup, error reporting for invalid pointer arguments, and build failure on unsupported Heimdal HDB versions.
