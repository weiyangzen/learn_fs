# File Research: sources/virtualization/spdk/lib/fsdev/Makefile

Builds the SPDK filesystem-device library.

Important behavior:
- Declares shared object version `4.0`.
- Builds `fsdev.c`, `fsdev_io.c`, and `fsdev_rpc.c`.
- Sets `LIBNAME = fsdev`.
- Uses `spdk_fsdev.map` as the symbol map.
- Includes common SPDK library make rules.

Role: build metadata for SPDK's fsdev abstraction, which is adjacent to virtualization/filesystem integration but whose implementation files are outside this grouped item.
