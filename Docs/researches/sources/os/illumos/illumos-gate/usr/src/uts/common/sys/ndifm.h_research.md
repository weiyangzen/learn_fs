# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/ndifm.h

NDI fault-management cache and error-dispatch interface.

Key responsibilities:
- Defines DMA and access handle cache type constants and default cache sizes.
- Declares default cache-size globals.
- Aliases DDI fault-management cache structures for NDI use.
- Defines per-handle `ndi_err_t` status with ENA, status, expected-error flag, ontrap pointer, FM cache entry link, and compare function.
- Under `_KERNEL`, declares FM cache insert/remove/error helpers, per-entry and all-entry error processing, FM handler dispatch, and access/DMA handle error setters.

Dependencies:
- Includes `sys/ddifm.h` and `sys/ddifm_impl.h`.

Notable risks:
- Error attribution depends on matching handles to FM cache entries correctly.
- Cache lifecycle must coordinate with device teardown and fault handler dispatch.
