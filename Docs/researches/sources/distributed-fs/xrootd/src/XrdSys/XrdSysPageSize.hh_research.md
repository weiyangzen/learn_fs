## sources/distributed-fs/xrootd/src/XrdSys/XrdSysPageSize.hh

Purpose: defines a uniform compile-time page size contract for XrdSys components.

Important APIs/types/functions: namespace constants `XrdSys::PageSize = 4096`, `PageMask = 4095`, and `PageBits = 12`.

Control flow: none.

State and persistence: none.

Dependencies and integration: no includes. Intended for components that need page alignment or page arithmetic without calling `getpagesize()`.

Risks: hard-coding 4 KiB is not universally correct across all architectures or filesystems. Code using this for kernel/user alignment must be validated on non-4K-page platforms.

Test signals: compile-time use in alignment math, runtime comparison with `sysconf(_SC_PAGESIZE)` on supported platforms, and behavior on systems with larger pages.
