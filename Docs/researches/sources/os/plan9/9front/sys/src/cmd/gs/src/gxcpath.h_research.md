# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gxcpath.h

Internal clipping list and clipping device definitions.

Key contents:
- Defines `gx_clip_rect`, a doubly linked rectangle with integer bounds and enumeration bookkeeping.
- Defines `gx_clip_list`, which is either a single rectangle or a linked list with dummy head/tail entries.
- Provides structure descriptor macros for clip rect/list GC support.
- Defines `clip_list_is_rectangle`.
- Defines `gx_device_clip`, a forwarding clipping device with clip list, current cursor, translation, cached clipping box, and target forwarding fields.
- Declares constructors for translated clip devices and clip-path devices.
- Declares clip-list initialization/freeing, outer-box setup, and rectangle-list access for clip paths.

Notable dependencies:
- Requires device-forwarding definitions from `gxdevice.h`.

Research notes:
- The header intentionally exposes implementation structs so clients can allocate clip lists/devices on the stack.
- Clip devices assume the target clipping box and clip list remain const after open because clipping box data is cached.
