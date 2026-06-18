# File Research: sources/local-fs/xfsprogs/libxfs/Makefile

Build rules for the static `libxfs.la` userspace library.

Key responsibilities:
- Defines package headers, internal headers, C sources, dummy C/C++ header-compile tests, and extra objects.
- Forces a static libtool build.
- Adds optional compile flags for `memfd_create` and nonblocking `getrandom`.
- Links against pthread, realtime, and libfrog libraries.
- Provides header installation targets for exported XFS headers.
- Generates dependency files, including extra dummy object dependencies.

Important behavior:
- `DEBUG = -DNDEBUG` intentionally avoids linking repair with a debug libxfs.
- Dummy C and C++ files test user-exported header compilability.
- Dependency includes are skipped under `NODEP`.

Dependencies:
- Includes top-level xfsprogs `builddefs` and `BUILDRULES`.
- Source list covers buffer/cache, transactions, allocation, btrees, attrs, dirs, realtime groups, metadir, parent pointers, and staging helpers.

Notable risks:
- Build correctness depends on long source/header lists staying synchronized with libxfs implementation growth.
