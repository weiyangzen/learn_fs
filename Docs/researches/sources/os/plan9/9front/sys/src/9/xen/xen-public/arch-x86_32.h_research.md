# File Research: sources/os/plan9/9front/sys/src/9/xen/xen-public/arch-x86_32.h

Imported Xen public 32-bit x86 compatibility include.

Purpose:
- Provides the legacy top-level 32-bit x86 public header path by including `arch-x86/xen.h`.

Key content:
- Contains license/comment header only, followed by `#include "arch-x86/xen.h"`.

Integration:
- The 9front Xen `mkfile` can choose this wrapper for older public-header layouts.
- The actual ABI definitions come from `arch-x86/xen.h` and its selected `xen-x86_32.h`.

Risks/notes:
- Small forwarding header, but include-path compatibility matters for generated Xen headers and source expecting the older public layout.
