# File Research: sources/virtualization/nvme-cli/libnvme/src/nvme/no-json.c

## Role

Build-time fallback for JSON configuration/tree APIs when JSON support is disabled.

## Behavior

- `json_read_config()`
- `json_update_config()`
- `json_dump_tree()`

All return `-ENOTSUP`.

## Dependencies

Includes `errno.h` and `libnvme.h`.

## Notes

This is a pure link-compatibility stub. No parsing, serialization, or tree traversal is attempted.
