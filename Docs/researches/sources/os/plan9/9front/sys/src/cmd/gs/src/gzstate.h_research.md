# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gzstate.h

Defines the private Ghostscript graphics state structure.

Key points:
- `gs_state_s` starts with `gs_imager_state_common`, making imager state the base layout.
- Stores saved-state chain, CTM inverse/default state, current path, clip path, clip stack, view clip, and effective clip cache.
- Holds color space, client color, and cached device color.
- Tracks current font, root font, character matrix, cachedevice/charpath modes, and show-state linkage.
- Stores gsave level, current device, device filter stack, transparency group stack, and client callbacks.
- Defines `gs_device_filter_stack_s` here so gstate lifecycle code can access reference counts.
- Provides GC descriptor declaration and `gs_state_do_ptrs` pointer enumeration macro.
- Defines `gx_setcurrentpoint` development macro.

Research notes:
- This is the internal state object tying paths, clipping, color, font, device, and transparency together.
- Device pointer handling is called out as special in GC enumeration.
