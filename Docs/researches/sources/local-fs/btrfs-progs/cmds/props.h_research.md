# File Research: sources/local-fs/btrfs-progs/cmds/props.h

## Purpose

Declares the property object model and handler interface used by `property.c`.

## Main Definitions

- `enum prop_object_type`
  - `prop_object_dev`
  - `prop_object_root`
  - `prop_object_subvol`
  - `prop_object_inode`

- `prop_handler_t`
  - Function pointer type for property handlers.
  - Receives object type, object path, property name, optional value, and force flag.

- `struct prop_handler`
  - `name`: property name.
  - `desc`: human-readable description.
  - `read_only`: whether the property can be set.
  - `types`: bitmask of supported object types.
  - `handler`: implementation callback.

## Exported Symbol

- `extern const struct prop_handler prop_handlers[];`

## Role in the Codebase

This header keeps the property dispatch table and object-type bitmask contract shared and explicit. The implementation is in `property.c`.
