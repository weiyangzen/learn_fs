# sources/user-network-fs/samba/source4/torture/ndr/odj.c

## Purpose

`odj.c` is a fixture for Windows Offline Domain Join provisioning data. It verifies that the generated ODJ NDR parser can pull a captured `ODJ_PROVISION_DATA_serialized_ptr` blob without error.

## Important APIs, Types, and Functions

- Includes `torture/ndr/ndr.h`, `librpc/gen_ndr/ndr_ODJ.h`, and `torture/ndr/proto.h`.
- `ODJ_PROVISION_DATA_data` embeds one serialized offline-join provisioning sample containing nested ODJ structures, Unicode strings, GUIDs, SID data, domain/controller names, and provisioning metadata.
- `ODJ_PROVISION_DATA_check()` receives `struct ODJ_PROVISION_DATA_serialized_ptr *` and currently returns `true` without semantic assertions.
- `ndr_ODJ_suite()` creates suite `ODJ` and registers one `torture_suite_add_ndr_pull_test()` for `ODJ_PROVISION_DATA_serialized_ptr`.

## Control Flow

The torture runner calls `ndr_ODJ_suite()`, which registers the static blob with the generated NDR pull framework. The framework decodes the blob into `ODJ_PROVISION_DATA_serialized_ptr` and then invokes `ODJ_PROVISION_DATA_check()`. Since the callback is a no-op success, the effective test result is pass/fail on parser acceptance and memory-safe traversal rather than field-level correctness.

## State and Persistence Behavior

There is no persistent state, no external I/O, and no mutable global state. All input is static in the binary, and decoded state is owned by the torture framework/TALLOC context.

## Dependencies and Integration Points

This file depends on generated ODJ NDR headers and the generic NDR torture helpers. It integrates with Samba's NDR test registry through `ndr_ODJ_suite()` and exercises the ODJ IDL-generated pull code rather than any live domain-join service.

## Risks and Edge Cases

- The check callback does not assert decoded domain names, SIDs, GUIDs, counts, pointer presence, or nested provisioning items. A parser could map fields incorrectly and still pass if it consumes the blob successfully.
- The fixture is a single captured example, so alternate ODJ versions, absent sections, malformed lengths, and error paths are not covered here.
- Because the data includes pointer-heavy serialized structures, changes in conformant-array or pointer semantics may produce broad failures that are hard to localize without additional assertions.

## Test Signals

The main signal is that `ODJ_PROVISION_DATA_serialized_ptr` can be unmarshalled from a realistic captured blob. Semantic test strength is low because `ODJ_PROVISION_DATA_check()` is empty. Future improvements should assert top-level counts, domain/computer strings, SID/GUID fields, and selected nested buffers.
