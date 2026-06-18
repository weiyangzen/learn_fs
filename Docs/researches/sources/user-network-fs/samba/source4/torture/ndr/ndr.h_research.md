# sources/user-network-fs/samba/source4/torture/ndr/ndr.h

## Purpose

`ndr.h` declares the shared public helper functions and registration macros used by Samba local NDR torture suites. It hides the repetitive work of binding a generated `ndr_pull_*`, `ndr_push_*`, and `ndr_print_*` routine to static fixture bytes and a typed validation callback.

## Important APIs, types, and functions

The public helpers are `_torture_suite_add_ndr_pullpush_test`, `_torture_suite_add_ndr_pull_inout_test`, and `_torture_suite_add_ndr_pull_invalid_data_test`. They accept generated pull/push/print function pointers, fixture `DATA_BLOB`s, structure sizes, NDR direction flags, libndr flags, callback names, and typed callback shims.

Macros include `torture_suite_add_ndr_pull_test`, `torture_suite_add_ndr_pull_invalid_data_test`, `torture_suite_add_ndr_pull_fn_test`, `torture_suite_add_ndr_pull_fn_test_flags`, `torture_suite_add_ndr_pull_validate_test`, `torture_suite_add_ndr_pull_validate_test_blob`, `torture_suite_add_ndr_pull_validate_test_b64`, `torture_suite_add_ndr_pullpush_fn_test_flags`, `torture_suite_add_ndr_pull_io_test`, and `torture_suite_add_ndr_pull_io_test_flags`.

## Control flow

The macros run at suite construction time. Each macro derives generated symbol names through token concatenation, wraps the typed checker in a `void *` callback cast, creates a constant or decoded `DATA_BLOB`, supplies `sizeof(struct name)`, and chooses the correct NDR flags. The actual execution control flow lives in `ndr.c`; this header establishes which wrapper is used and whether push validation, direction-specific pull, NDR64, base64 fixture decoding, or in/out two-phase decoding will occur.

## State and persistence

There is no persistent state. The header only constructs registrations. Base64 fixture macros allocate decoded blobs on the suite talloc context, so their lifetime is tied to the suite. Other fixture macros wrap static arrays with `data_blob_const`.

## Dependencies

The header includes `torture/torture.h`, `librpc/ndr/libndr.h`, and `libcli/security/security.h`. It depends on generated NDR naming conventions: for a structure `name`, `ndr_pull_name`, `ndr_push_name`, and `ndr_print_name` must exist with compatible signatures.

## Integration points

Every protocol-specific file in this subset uses these macros to register tests. The macros are the compatibility layer between generated NDR code and the torture framework, so changes here affect all local NDR fixture suites.

## Risks

The macros rely on unchecked function pointer casts from typed callbacks to `void *` callbacks. This is a common C test-harness pattern but gives compile-time checking only inside the temporary typed assignment, not at the final stored callback call site. Token concatenation also means generated symbol naming must remain exact. Pull-only macros do not test encoder round trips. The base64 macro allocates during suite creation and assumes decoding succeeds; failed allocation or malformed base64 would surface later through the helper.

## Test signals

The header itself is not executable, but it defines the signal strength of downstream tests. Validate macros supply both pull and push functions and therefore enable byte-for-byte round-trip checks. Direction macros make `NDR_IN`, `NDR_OUT`, and `LIBNDR_FLAG_NDR64` explicit in test names. In/out macros preserve request context before decoding response fixtures.
