# File Research: sources/os/plan9/9front/sys/src/9/xen/xen-public/xen-compat.h

Purpose: Xen public compatibility shim. It defines the latest supported interface version and default behavior for guests/tools that do not select an interface version.

Key interfaces:
- `__XEN_LATEST_INTERFACE_VERSION__` set to `0x00040300`.
- Tools/hypervisor builds force `__XEN_INTERFACE_VERSION__` to latest.
- Guests without a requested version get legacy `0x00000000`.
- Compile-time rejection if a requested version is newer than the headers.

Integration notes: Included first by `xen.h`, which drives many version conditionals in other public headers.

Risk/attention points: Changing this file affects ABI selection across the entire Xen header set.
