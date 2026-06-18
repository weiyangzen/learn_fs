## sources/distributed-fs/xrootd/src/XrdSys/XrdSysPlatform.cc

Purpose: implements portability helpers declared in `XrdSysPlatform.hh`.

Important APIs/types/functions: `Swap_n2hll()` is provided for little-endian platforms lacking GCC byte-swap support or on Apple; fallback `strlcpy()` is implemented when `HAVE_STRLCPY` is absent; `XrdSys::getIovMax()` returns the maximum supported iovec count, using `sysconf(_SC_IOV_MAX)` when `IOV_MAX` is unavailable.

Control flow: compile-time endianness and feature checks select helper definitions. `getIovMax()` uses a static lambda-backed value when it must query `sysconf`, defaulting to 1024 if the query fails.

State and persistence: no mutable external state except static cached `IOV_MAX` inside `getIovMax()` on platforms needing runtime discovery.

Dependencies and integration: uses byte-order/network conversion headers, C string routines, and `sysconf`. Used by logging and I/O vector code.

Risks: strict-aliasing/alignment assumptions in `Swap_n2hll()` can be sensitive. Fallback `strlcpy()` assumes `sz > 0` before writing `dst[0]` in one branch. `IOV_MAX` macro shadowing by static local name is unusual.

Test signals: endian conversion round trips, fallback `strlcpy()` boundary sizes including zero, `getIovMax()` with and without `IOV_MAX`, and builds on Apple/non-GCC little-endian targets.
