# sources/user-network-fs/samba/source4/torture/libnet/domain.c

## Purpose

`domain.c` tests the libnet convenience API for opening a SAMR domain handle and then closing it through raw SAMR.

## Important APIs, Types, and Functions

- `test_domainopen()` prepares `struct libnet_DomainOpen` with the workgroup domain name and `SEC_FLAG_MAXIMUM_ALLOWED`.
- `test_cleanup()` closes the returned domain handle with `dcerpc_samr_Close_r()`.
- `torture_domainopen()` initializes a libnet context, connects to SAMR, and runs open/close.

## Control Flow

The test creates a memory context and libnet context, opens an RPC connection to the SAMR interface, uses `lpcfg_workgroup()` as the domain name, calls `libnet_DomainOpen()`, stores the returned handle, and closes it via SAMR.

## State and Persistence Behavior

No persistent domain state is changed. The only server-side state is a transient SAMR policy handle, which the test closes.

## Dependencies and Integration Points

It depends on `libnet_context_init()`, `libnet_DomainOpen()`, SAMR NDR client bindings, `torture_rpc_connection()`, and loadparm workgroup configuration. It is registered as `net.domopen` by `libnet.c`.

## Risks and Edge Cases

The test assumes the configured workgroup names a SAMR domain reachable over the torture RPC connection. Failure to close handles would leak server resources until connection teardown. Access mask or domain name behavior changes in libnet can break the test.

## Test Signals

Success is `NT_STATUS_OK` for the SAMR connection, libnet domain open, and SAMR close result. Diagnostics identify domain-open or close failures.
