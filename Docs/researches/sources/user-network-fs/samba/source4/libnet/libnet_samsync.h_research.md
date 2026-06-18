# sources/user-network-fs/samba/source4/libnet/libnet_samsync.h

## Purpose

`libnet_samsync.h` declares a small request/response structure for dumping SAM data into a keytab-like output path. In this subset it is only a contract header; the implementation is elsewhere.

## Important APIs, Types, and Functions

`struct libnet_SamDump_keytab` contains input `binding_string`, `keytab_name`, and `machine_account` credentials, plus output `error_string`.

## Control Flow

No code executes here. Callers populate the structure and pass it to the SAM dump/keytab implementation.

## State and Persistence Behavior

The intended persistent output is the named keytab file. The structure itself only stores pointers and an error string.

## Dependencies and Integration Points

The header includes generated NETLOGON types and references `struct cli_credentials`. It conceptually fits the libnet replication/secrets export area, alongside vampire and keytab export code.

## Risks and Edge Cases

The binding string and machine account must represent a secure, authorized channel; misuse risks exporting sensitive key material. The header does not express ownership or validation rules.

## Test Signals

Useful signals are integration tests that attempt a SAM dump to a temporary keytab and verify both success and authorization failure paths without leaving stale key material.
