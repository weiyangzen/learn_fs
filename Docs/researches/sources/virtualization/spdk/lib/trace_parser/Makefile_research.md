# File Research: sources/virtualization/spdk/lib/trace_parser/Makefile

This Makefile builds the `trace_parser` SPDK library.

It sets `SPDK_ROOT_DIR`, includes common SPDK make rules, declares shared-library version `SO_VER := 8` and `SO_MINOR := 0`, compiles `trace.cpp` as the C++ source, names the library `trace_parser`, links `-lrt`, uses `spdk_trace_parser.map`, and includes the standard SPDK library makefile.

The library is a small standalone parser component for trace shared-memory/files rather than part of the trace writer hot path.
