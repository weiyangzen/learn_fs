# sources/user-network-fs/samba/source4/dsdb/gmsa/gkdi.h

## Purpose

`gkdi.h` declares the DSDB-facing GKDI root-key API used by gMSA code. It exposes conversion from LDB root-key messages to crypto objects, root-key use-start-time calculation, root-key creation, lookup by GUID, and lookup of the most recent usable root key.

## Important APIs, Types, and Functions

- Forward declarations: `struct ldb_message`, `struct ldb_context`, and `struct ProvRootKey`.
- `gkdi_root_key_from_msg()` converts a root-key LDB message and known GUID into a `ProvRootKey`.
- `gkdi_root_key_use_start_time()` calculates a protocol-oriented use start time from a current time.
- `gkdi_new_root_key()` creates and returns a new root-key LDB message.
- `gkdi_root_key_from_id()` reads a root-key LDB message by GUID.
- `gkdi_most_recently_created_root_key()` selects a usable key by time bounds.

## Control Flow

The header does not implement control flow. It defines the boundary between DSDB/LDB storage and crypto derivation. Callers generally fetch a message with one of the LDB-returning functions and then call `gkdi_root_key_from_msg()` to obtain a `ProvRootKey` suitable for password derivation.

## State and Persistence Behavior

The API implies two ownership patterns: returned `struct ldb_message` pointers are talloc-owned by the caller-supplied memory context, while returned `ProvRootKey` objects are also caller-owned. `gkdi_new_root_key()` is the only declared function that creates persistent directory state.

## Dependencies and Integration Points

The header includes talloc, `DATA_BLOB`, time, NTSTATUS, and GUID definitions. It is consumed by `gmsa/util.c` and implemented by `gkdi.c`.

## Risks

Because this header hides LDB details behind integer return codes for lookup/create functions and NTSTATUS for conversion, callers must handle both LDB and NTSTATUS error domains. Future changes to root-key selection semantics need coordinated changes in both `gkdi.c` and gMSA rollover logic.

## Test Signals

Compile/link tests should verify that all declared functions are implemented. Behavioral tests should focus through `gkdi.c` and `gmsa/util.c`: creation, lookup, no-key errors, and conversion to `ProvRootKey`.
