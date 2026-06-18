# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/exacct.h

## Role

`exacct.h` is the main extended accounting API header. It defines exacct versioning, syscall options, libexacct error codes, object model types, object manipulation functions, and kernel accounting assembly/commit hooks.

## Public ABI

- Defines `EXACCT_VERSION` 1.
- Defines unpack allocation modes `EUP_ALLOC` and `EUP_NOALLOC`, coordinated with `ea_free_object()`.
- Defines record type options `EW_PARTIAL`, `EW_INTERVAL`, and kernel-only `EW_FINAL`.
- Defines `EP_RAW` and `EP_EXACCT_OBJECT` to distinguish raw buffers from packed exacct objects.
- Limits accounting buffers with `EXACCT_MAX_BUFSIZE` at 64 KiB.
- Userland syscall prototypes are `getacct()`, `putacct()`, and `wracct()`.
- Defines libexacct result codes from `EXR_OK` through `EXR_INVALID_OBJ`.

## Object Model

- `ea_size_t` is 64-bit; `ea_catalog_t` is 32-bit.
- `ea_object_type_t` distinguishes errors, empty objects, groups, and items.
- `ea_item_t` stores scalar, string, embedded object, or raw payload plus payload size.
- `ea_group_t` stores object count and pointer to child object list.
- `ea_object_t` combines type, group/item union, sibling link, and catalog tag.
- Accessor macros expose item union fields (`ei_uint64`, `ei_string`, etc.) and object union fields (`eo_group`, `eo_item`).

## Functions

The public object API includes `ea_set_item()`, `ea_set_group()`, attachment functions, `ea_free_item()`, `ea_free_object()`, `ea_pack_object()`, and allocation/string helpers.

Under `_KERNEL`, the header declares allocation helpers, process/task/flow/net accounting commit and assembly routines, header creation/write functions, task mstate movement, the `exacct_queue` taskq, and `exacct_object_cache`.
