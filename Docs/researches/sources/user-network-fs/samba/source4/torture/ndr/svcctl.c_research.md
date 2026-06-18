# sources/user-network-fs/samba/source4/torture/ndr/svcctl.c

## Purpose

`svcctl.c` validates NDR parsing for the Service Control Manager `ChangeServiceConfigW` request and response. It focuses on a captured request that changes service type/start/error-control fields while leaving optional strings and dependency/password fields null.

## Important APIs, Types, and Functions

- Includes `librpc/gen_ndr/ndr_svcctl.h`, `torture/ndr/ndr.h`, `torture/ndr/proto.h`, and `param/param.h`.
- `svcctl_ChangeServiceConfigW_req_data` is the request fixture.
- `svcctl_ChangeServiceConfigW_req_check()` builds an expected `policy_handle` UUID with `GUID_from_string()`, then asserts handle UUID, service type, `SVCCTL_AUTO_START`, `SVCCTL_SVC_ERROR_NORMAL`, null optional strings, null `tag_id`, and zero dependency/password sizes.
- `svcctl_ChangeServiceConfigW_rep_data` is the response fixture.
- `svcctl_ChangeServiceConfigW_rep_check()` asserts null output `tag_id` and `WERR_OK`.
- `ndr_svcctl_suite()` registers request and response pull tests for `svcctl_ChangeServiceConfigW`.

## Control Flow

The suite constructor creates suite `svcctl`, registers the request blob as `NDR_IN` with the request check callback, then registers the response blob as `NDR_OUT` with the response check callback. The request callback is linear and covers every decoded input field present in the call shape. The response callback covers the output pointer and result status.

## State and Persistence Behavior

No service is contacted or modified. The service handle and configuration fields are static captured wire data. Decoded objects are transient inside the torture framework.

## Dependencies and Integration Points

This test integrates the generated SVCCTL NDR parser with Samba's NDR torture harness. It depends on GUID parsing, service-control constants, WERROR assertions, and generated `struct svcctl_ChangeServiceConfigW` direction-specific members.

## Risks and Edge Cases

- Coverage is limited to one operation and one shape of optional-field usage.
- It validates null optional fields well, but does not cover non-null binary path, dependencies multi-string handling, password buffers, display names, or failure statuses.
- `GUID_from_string()` return status is not asserted before using the UUID, although the literal is fixed and expected to parse.

## Test Signals

This file gives a strong semantic signal for one `ChangeServiceConfigW` request/response pair: field-level assertions cover handle identity, enum values, null pointers, size fields, and success status. It is narrow but precise.
