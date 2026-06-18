<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-utils/utils/mount/parse_opt.h -->
# sources/user-network-fs/nfs-utils/utils/mount/parse_opt.h

## Purpose

`parse_opt.h` is the public interface for the mount-option list abstraction. It hides the linked-list representation and gives mount code a small API for parsing, querying, editing, and serializing option strings.

## Important APIs, types, and functions

The header defines `po_return_t` (`PO_FAILED`, `PO_SUCCEEDED`) and `po_found_t` (`PO_NOT_FOUND`, `PO_FOUND`, `PO_BAD_VALUE`). It forward-declares `struct mount_options` and declares all list lifecycle, lookup, mutation, and serialization functions implemented in `parse_opt.c`.

## Control flow

There is no executable control flow. The API contract implies a parse-edit-join lifecycle: obtain a handle with `po_split`, modify with insert/append/remove/replace, query with contains/get/rightmost, serialize with `po_join`, then release with `po_destroy`.

## State and persistence behavior

The opaque handle represents heap state managed by the implementation. The header itself stores no state and performs no persistence. Callers are responsible for freeing joined strings as documented by `po_join` behavior.

## Dependencies and integration points

The header is included by `stropts.c`, `utils.c`, and other mount helpers. Because the representation is opaque, callers cannot depend on list internals and must use the exported functions for all option manipulation.

## Risks and edge cases

The API uses mutable `char *` for many input strings even when functions do not modify the caller buffer, which can invite casts from const data. `po_get` returns an interior pointer owned by the option list, so callers must not free or retain it beyond list lifetime.

## Test signals

Compile tests should ensure all mount users include this header without requiring private structs. API tests should verify that returned `po_found_t` values distinguish absent options from bad numeric options.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-utils/utils/mount/parse_opt.h -->
