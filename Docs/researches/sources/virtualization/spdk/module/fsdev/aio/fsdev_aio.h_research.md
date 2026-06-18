# File Research: sources/virtualization/spdk/module/fsdev/aio/fsdev_aio.h

Declares the public AIO fsdev module interface.

Key elements:
- `struct spdk_fsdev_aio_opts` contains xattr, writeback cache, max write, and skip read/write options.
- Defines async delete completion callback type.
- Declares default option population, create, and delete functions.

Dependencies:
- Includes SPDK fsdev module header.

Research notes:
- Used by RPC code and the module implementation.
