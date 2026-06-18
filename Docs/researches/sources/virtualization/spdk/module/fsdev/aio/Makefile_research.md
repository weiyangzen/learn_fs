# File Research: sources/virtualization/spdk/module/fsdev/aio/Makefile

Builds the AIO fsdev module.

Key elements:
- Compiles `fsdev_aio.c` and `fsdev_aio_rpc.c`.
- On Linux, compiles `linux_aio_mgr.c` and links `-laio`.
- On non-Linux, compiles POSIX `aio_mgr.c`.
- Produces `fsdev_aio`.
- Uses shared object version `3.0`.

Dependencies:
- Uses blank SPDK map file and standard SPDK library make infrastructure.

Research notes:
- Selects between Linux libaio and portable POSIX AIO manager implementations.
