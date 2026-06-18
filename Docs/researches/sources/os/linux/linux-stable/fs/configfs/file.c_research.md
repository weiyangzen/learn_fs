# File Research: sources/os/linux/linux-stable/fs/configfs/file.c

This file implements configfs regular text attributes and binary attributes.

Key responsibilities:
- Defines `struct configfs_buffer`, the per-open file state for configfs attributes.
- Implements text attribute read/write via `show()` and `store()` callbacks.
- Implements binary attribute buffered reads and writes via `read()` and `write()` callbacks.
- Creates attribute dirents for items through `configfs_create_file()` and `configfs_create_bin_file()`.

Important control flow:
- Text reads allocate a 4 KiB page and call `attr->show()` under fragment read lock unless the fragment is dead.
- Text writes copy at most `SIMPLE_ATTR_SIZE - 1`, NUL-terminate the buffer, then call `attr->store()`.
- Binary reads first query size with `read(item, NULL, 0)`, enforce `cb_max_size`, allocate a vmalloc buffer, then perform a second read to fill it.
- Binary writes grow a vmalloc buffer as offsets advance and defer the actual callback write until file release.
- `__configfs_open_file()` validates fragment liveness, item/attribute presence, module ownership, permissions, and required callbacks.
- Release drops the module reference and frees buffers.

Dependencies:
- Uses `configfs_fragment` from directory lifecycle to prevent operations after teardown.
- Attribute metadata comes from public configfs item types and `configfs_attribute` / `configfs_bin_attribute`.

Risks and invariants:
- Text attributes are limited to 4096 bytes regardless of architecture page size.
- Binary attributes do not support switching between read and write modes in the same open file.
- Binary `release()` ignores the callback result by design.
- Fragment death changes operations to `-ENOENT`, preventing callbacks into detached objects.
