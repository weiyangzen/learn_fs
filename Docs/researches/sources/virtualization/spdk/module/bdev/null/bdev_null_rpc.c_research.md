# File Research: sources/virtualization/spdk/module/bdev/null/bdev_null_rpc.c

This file exposes the null bdev module through JSON-RPC. It registers `bdev_null_create`, `bdev_null_delete`, and `bdev_null_resize` runtime RPCs and maps autogen RPC request structs into `null_bdev_opts`.

`bdev_null_create` decodes required name, block count, and block size plus optional UUID, physical block size, metadata/DIF fields, and preferred write/unmap fields. It passes those options to `bdev_null_create()` and returns the created bdev name on success. Decoded strings and autogen-owned fields are freed on all paths.

`bdev_null_delete` decodes the name and calls asynchronous `bdev_null_delete()`. Its callback returns JSON `true` on success or a JSON-RPC error with `spdk_strerror()`. `bdev_null_resize` decodes name and `new_size`, calls `bdev_null_resize()`, and returns a boolean.

The main risk surface is parameter validation split between RPC decode and `bdev_null_create()`/`resize()`: RPC mostly checks JSON shape, while semantic checks such as block alignment, DIF validity, ownership, and shrinking are enforced in the module.
