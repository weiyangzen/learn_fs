# sources/user-network-fs/samba/source4/torture/ndr/winreg.c

## Purpose

`winreg.c` is a broad NDR torture fixture for Windows Remote Registry RPC operations. It decodes captured request/response blobs for key open/close/create/delete/flush/query/enumeration/notification APIs and asserts selected handle, string, buffer, metadata, and result-code fields.

## Important APIs, Types, and Functions

- Includes `librpc/gen_ndr/ndr_winreg.h`, `librpc/gen_ndr/ndr_security.h`, `libcli/security/security.h`, and generic NDR torture helpers.
- Fixtures cover `winreg_CloseKey`, `OpenHKLM`, `CreateKey`, `EnumValue`, `QueryValue`, `QueryMultipleValues`, `QueryMultipleValues2`, `FlushKey`, `OpenKey`, `DeleteKey`, `GetVersion`, `QueryInfoKey`, `NotifyChangeKeyValue`, and `EnumKey`.
- Disabled fixtures/checks exist for `QueryInfoKey` output and `GetKeySecurity` input/output.
- Check callbacks validate details such as policy-handle presence/type, `OpenHKLM` system/access mask, key name `spottyfoot`, value name `HOMEPATH`, value name `TEMP`, type/size/length pointers, `WERR_INVALID_PARAMETER`, `WERR_FILE_NOT_FOUND`, `WERR_MORE_DATA`, version `5`, notify flags, and enum-key metadata.
- `ndr_winreg_suite()` registers the fixtures with `torture_suite_add_ndr_pull_fn_test()` or `torture_suite_add_ndr_pull_io_test()`.

## Control Flow

The suite constructor is a linear registration table. Each operation gets one or more direction-specific tests. Simple request/response cases use separate `NDR_IN` and `NDR_OUT` registrations; buffer-negotiating calls such as `QueryMultipleValues` and `QueryMultipleValues2` use pull-IO tests pairing request and response fixtures. Some fixtures are registered with `NULL` callbacks when decode-only coverage is intended, such as one alternate `EnumValue` input.

Callbacks are operation-specific and generally validate the highest-value decoded fields without trying to model registry semantics. Several comments mark known gaps such as unchecked parent handles, output buffers, or last-change timestamps.

## State and Persistence Behavior

The file does not access a live registry and does not persist any key/value changes. All registry handles, names, classes, data buffers, security descriptors, and result codes are captured byte arrays. Decoded state is transient and owned by the torture runner.

## Dependencies and Integration Points

This file integrates generated winreg NDR types with the torture framework and security helpers. It depends on WERROR constants, GUID-zero checks, registry string containers, buffer-size pointer semantics, and generated request/response unions. It is a compatibility layer test for Samba's remote-registry marshalling contract, not the registry server implementation.

## Risks and Edge Cases

- Some important semantic fields are explicitly marked `FIXME`, including parent handles, some output buffers, and timestamps.
- `QueryInfoKey` output and `GetKeySecurity` tests are disabled, so security descriptor and key-info response coverage is incomplete.
- Several tests assert pointer presence and sizes but not the full pointed-to buffer content.
- Captured pointer-looking values and historical Windows layouts can be brittle if generated IDL alignment or pointer policy changes.

## Test Signals

The suite provides good breadth across remote-registry NDR operations and moderate semantic depth for key names, value names, buffer sizing, and result codes. Stronger signals come from `EnumValue`, `QueryValue`, `QueryMultipleValues`, `OpenKey`, `DeleteKey`, `NotifyChangeKeyValue`, and `EnumKey` callbacks. Weaker areas are disabled security/key-info responses and callbacks that intentionally leave handle/buffer validation as future work.
