# sources/user-network-fs/samba/source4/torture/rpc/ntsvcs.c

## Purpose

`ntsvcs.c` defines a compact RPC torture suite for the Windows Plug and Play/NT services RPC interface represented by `ndr_table_ntsvcs`. It probes a small set of PNP calls and validates basic marshalling, expected error codes, and buffer sizing behavior.

## Important APIs, Types, and Functions

The suite factory is `torture_rpc_ntsvcs()`, which registers four tests:

- `test_PNP_GetVersion()`: calls `PNP_GetVersion` and expects version `0x400`.
- `test_PNP_GetDeviceListSize()`: calls `PNP_GetDeviceListSize` first with a null device/service name expecting `WERR_CM_INVALID_POINTER`, then with `"Spooler"` expecting success.
- `test_PNP_GetDeviceList()`: calls `PNP_GetDeviceList` with a null filter expecting `WERR_CM_INVALID_POINTER`; then queries `"Spooler"`, handles `WERR_CM_BUFFER_SMALL` by asking for the required length, allocates the buffer, and retries.
- `test_PNP_GetDeviceRegProp()`: queries `DEV_REGPROP_DESC` for a hard-coded ACPI path and retries with the reported `needed` size if the first call reports `WERR_CM_BUFFER_SMALL`.

All calls are generated DCERPC client calls against `struct dcerpc_binding_handle *b = p->binding_handle`.

## Control Flow

Each test initializes the relevant NDR request structure, fills in input and output pointer fields, performs the generated RPC call, and asserts both transport-level NTSTATUS and operation-level WERROR. Buffer-sized calls intentionally start with minimal buffers to exercise the server's size-reporting path before retrying with allocated storage.

## State and Persistence Behavior

The tests are read-only from the server's perspective. They allocate temporary buffers from `tctx` with talloc and do not store process-global state. The only mutable values are local output scalars such as `version`, `size`, `length`, `needed`, and registry data type.

## Dependencies and Integration Points

The file depends on the Samba torture RPC framework and generated `ndr_ntsvcs_c.h` bindings. It integrates into the RPC torture registry under suite name `ntsvcs` and uses `torture_suite_add_rpc_iface_tcase()` for a plain RPC interface testcase.

## Risks and Edge Cases

The hard-coded `"Spooler"` service and `ACPI\\ACPI0003\\1` device path are environment-sensitive. The tests mostly assert call mechanics and some known Windows-compatible behavior, but device-registry data may vary by target.

`test_PNP_GetDeviceRegProp()` returns true after retrying and does not assert the final WERROR; it primarily guards transport success and buffer-retry behavior rather than property presence.

## Test Signals

Useful signals include exact `WERR_CM_INVALID_POINTER` for null device/filter inputs, successful size and list calls for `"Spooler"`, successful handling of `WERR_CM_BUFFER_SMALL`, and `PNP_GetVersion` returning `0x400`.
