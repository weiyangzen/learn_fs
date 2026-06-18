# sources/user-network-fs/samba/source4/libnet/libnet_export_keytab.h

## Purpose
`libnet_export_keytab.h` declares the request/result structure and function prototype for exporting Samba KDC keys into a Kerberos keytab.

## Important APIs, Types, And Functions
`struct libnet_export_keytab` has inputs `keytab_name`, optional `principal`, optional `samdb`, `keep_stale_entries`, `only_current_keys`, and `as_for_AS_REQ`. Output is `error_string`. The public function is `NTSTATUS libnet_export_keytab(struct libnet_context *ctx, TALLOC_CTX *mem_ctx, struct libnet_export_keytab *r)`.

## Control Flow
The header exposes two modes: a specific principal export when `principal` is non-null, and complete domain export when it is null. Flags influence whether stale keytab entries are retained, whether historic keys are exported, and whether KDC lookup uses AS-REQ semantics or administrative data semantics.

## State And Persistence Behavior
The structure identifies the keytab file that will be modified by the implementation and the database context to read from. The header itself has no persistence logic.

## Dependencies And Integration Points
The header includes `includes.h` and `libnet/libnet.h`, and references `struct ldb_context` for optional database input. It is used by command or provisioning paths that need service keys in a keytab.

## Risks
Callers must treat `keytab_name` as a write target containing secrets. Passing `principal == NULL` requests broad export. Misunderstanding `only_current_keys` or `keep_stale_entries` can either omit keys needed during rollover or retain unwanted old keys.

## Test Signals
API-level tests should verify all inputs are honored by `libnet_export_keytab.c`, especially null principal mode, `samdb` time handling for gMSA keys, and `error_string` population on failure.
