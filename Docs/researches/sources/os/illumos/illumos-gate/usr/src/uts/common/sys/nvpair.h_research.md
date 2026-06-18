# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/nvpair.h

## Purpose

`nvpair.h` defines the public illumos name-value pair and name-value list API used across kernel and userland for typed property lists, packing/unpacking, lookup, mutation, and fail-fast convenience wrappers.

## Main Interfaces

`data_type_t` enumerates supported value types: booleans, bytes, signed/unsigned integer widths, strings, arrays, hrtime, nested nvlist, nvlist arrays, and userland-only double. Kernel builds omit `DATA_TYPE_DOUBLE`.

`nvpair_t` defines the packed pair header: size, name size, element count, and type, followed by name and aligned value data. `nvlist_t` defines list header fields: version, persistent flags, private implementation pointer, runtime flags, and padding.

Constants define version, native/XDR encoding, uniqueness flags, lookup flags, alignment helpers, and macros for pair/list field access.

The allocator framework consists of `nv_alloc_t`, `nv_alloc_ops_t`, fixed/nosleep/sleep allocators, and init/reset/fini functions.

The main API covers allocation/free, size, pack/unpack, dup, merge, custom allocator variants, add/remove operations for every supported type, lookup operations for every supported type, pair existence/emptiness checks, pair iteration, pair field accessors, and value extraction from `nvpair_t`.

The `fnvlist_*` and `fnvpair_*` family provides fail-fast convenience wrappers that return values directly or abort/panic on allocation/lookup failure depending on environment.

## Runtime Use

Callers allocate an `nvlist_t`, add typed name-value pairs, optionally pack it for transport/storage, unpack it later, and look up values by name and type. Kernel callers can choose sleep/nosleep allocation behavior; userland can use allocator variants or defaults.

## Dependencies

Includes `sys/types.h`, `sys/time.h`, `sys/errno.h`, and `sys/va_list.h`. Kernel non-boot builds include `sys/kmem.h`.

Implementation-private details live in `nvpair_impl.h`.

## Risks and Invariants

The on-wire/in-memory packed layout depends on alignment macros and type enum values. Changes can break native/XDR compatibility.

The `NVL_SIZE(nvl)` macro references `nvl_size`, which is not a member of the visible `nvlist_t`; it likely applies only to packed/internal layouts and should be used carefully.

String and array lookup APIs return pointers owned by the nvlist; callers must not free or outlive the list unless documented by implementation behavior.

Fail-fast `fnvlist_*` wrappers are convenient but inappropriate where recoverable allocation or missing-key errors must be surfaced.
