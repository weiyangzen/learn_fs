# File Research: sources/virtualization/spdk/module/sock/posix/Makefile

Builds the POSIX socket implementation module.

Key elements:
- Compiles `posix.c`.
- Produces `sock_posix`.
- Links `-lssl`.
- Uses shared object version `8.0`.
- Uses blank SPDK map file.

Dependencies:
- Built through SPDK library make infrastructure.

Research notes:
- The listed group includes only this Makefile, not `posix.c`; it establishes POSIX socket module build metadata.
