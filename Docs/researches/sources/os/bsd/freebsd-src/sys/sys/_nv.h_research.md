# File Research: sources/os/bsd/freebsd-src/sys/sys/_nv.h

Name-value list forward declaration.

Key elements:
- Includes `sys/nv_namespace.h` outside the kernel.
- Forward-declares `struct nvlist`.
- Defines `nvlist_t` once via `_NVLIST_T_DECLARED`.

Dependencies:
- Userland namespace handling through `sys/nv_namespace.h`.

Research notes:
- Keeps consumers from needing the full nvlist layout.
- Used where typed references to libnv/kernel nvlist objects are enough.
