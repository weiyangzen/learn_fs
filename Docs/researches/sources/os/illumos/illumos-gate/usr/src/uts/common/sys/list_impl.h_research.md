# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/list_impl.h

## Role

Concrete layout backing `sys/list.h`.

## Structure

Defines `struct list_node` with next/previous pointers and `struct list` with element size, node offset, and sentinel head node.

## Dependencies And Consumers

Includes `sys/types.h` for `size_t`. Direct consumers are the list implementation and code that needs the concrete list layout, usually through `sys/list.h`.

## Important Details

The sentinel node is embedded in `struct list`, so an empty list does not require allocation. ABI/layout consumers rely on `list_size` and `list_offset` matching `list_create()` expectations.

## Research Notes

Read completely: 51 lines, 1293 bytes.
