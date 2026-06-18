<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/cifs-utils/cifs_spnego.h -->
# sources/user-network-fs/cifs-utils/cifs_spnego.h

## Purpose

`cifs_spnego.h` defines the userspace/kernel packet contract for CIFS SPNEGO upcalls.

## Important APIs, Types, and Functions

The key constant is `CIFS_SPNEGO_UPCALL_VERSION`, currently `2`. `struct cifs_spnego_msg` contains `version`, `flags`, `sesskey_len`, `secblob_len`, and flexible payload storage in `data[1]`, where callers concatenate session key bytes followed by the security blob.

## Control Flow

`cifs.upcall.c` fills this structure after obtaining Kerberos/GSS material and passes it to `keyctl_instantiate`. The kernel CIFS key type interprets the same layout.

## State and Persistence Behavior

The header defines an in-memory wire format stored in kernel key payloads. It has no independent state.

## Dependencies and Integration Points

It depends on fixed-width integer types from surrounding includes and conditionally declares the kernel key type under `__KERNEL__`. It is a compatibility boundary between cifs-utils and the Linux CIFS client.

## Risks and Edge Cases

Changing field order, version, or payload packing would break kernel/userspace compatibility. `data[1]` is the classic flexible-array idiom, so allocation must include both variable-length regions.

## Test Signals

Tests should validate packet size calculation, version checks, zero-length fields, and kernel acceptance of generated key payloads from `cifs.upcall`.
<!-- END_FILE_RESEARCH: sources/user-network-fs/cifs-utils/cifs_spnego.h -->
