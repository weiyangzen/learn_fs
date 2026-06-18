# File Research: sources/os/bsd/dragonflybsd/sys/sys/rman.h

This header defines DragonFly BSD's resource manager interface for managing allocatable bus/resource address ranges and exporting resource manager state to userland.

Key responsibilities:
- Defines `RF_*` resource flags:
  - allocated, active, shareable, timeshare, wanted, first-share, prefetchable, optional
  - encoded alignment fields with `RF_ALIGNMENT_*`
- Defines `enum rman_type`:
  - `RMAN_UNINIT`
  - `RMAN_GAUGE`
  - `RMAN_ARRAY`
- Defines user-exported `struct u_resource` and `struct u_rman` with stable text length `RM_TEXTLEN`.
- Defines kernel `struct resource`:
  - resource range start/end
  - flags and optional RID
  - virtual address
  - bus space tag/handle
  - owning device
  - parent `struct rman`
  - links for resource and share lists
- Defines kernel `struct rman`:
  - managed resource list
  - sleep/token lock pointer
  - global rman list link
  - start/end range
  - type, description, owner CPU, destruction interlock
- Declares kernel APIs for initialization, region management, reservation, activation, deactivation, release, finish, and alignment flag construction.
- Provides accessor macros for resource fields.

Important invariants:
- Resources use linked lists instead of bitmaps so huge address spaces can be represented.
- Resource indexes are `u_long`, matching the historical design intent for large resource spaces.
- Resource ranges are inclusive; size is `r_end - r_start + 1`.
- `rm_cpuid` tracks ownership for DragonFly's per-CPU/resource-manager model.

Research notes:
- This is a kernel bus resource allocation contract with a small user-visible reporting ABI.
- `rman_await_resource()` is present only inside `#if 0`.
