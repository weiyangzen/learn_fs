# File Research: sources/virtualization/spdk/app/trace/Makefile

This makefile builds the C++ `spdk_trace` tool from `trace.cpp`. It includes SPDK common and module definitions, sets `APP = spdk_trace`, and sets `SPDK_NO_LINK_ENV = 1`.

`SPDK_NO_LINK_ENV = 1` is important because the source intentionally avoids linking the full SPDK environment implementation. The makefile links `json` and `trace_parser`, while the source provides small aborting/no-op stubs for environment functions that are pulled in indirectly by utility code but not used by the tool's trace parsing path.

The build uses `CXX_SRCS := trace.cpp` and includes `mk/spdk.app_cxx.mk`. Install and uninstall use standard SPDK app macros.
