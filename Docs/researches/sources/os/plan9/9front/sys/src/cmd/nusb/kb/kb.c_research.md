# File Research: sources/os/plan9/9front/sys/src/cmd/nusb/kb/kb.c

This file implements the USB HID keyboard, mouse, touchpad, touchscreen, and tablet input bridge. It reads HID interrupt reports, parses them against HID report descriptors, translates keyboard usages to Plan 9 scan codes sent to `/dev/kbin`, translates pointer/touch data to mouse(3) messages sent to `/dev/mousein`, and serves a small control file for repeat timing, debug, and raw output reports.

Descriptor handling first tries to fetch the HID report descriptor. If missing for boot keyboard or boot pointer devices, it uses built-in boot descriptors. `setproto()` also sends `SET_IDLE` and switches boot-mode devices to either boot or report protocol as appropriate. Device quirks override or patch descriptors for a Gaomon S620 tablet and an Elecom trackball.

The HID parser recursively walks collections and fields, preserving global/local state and invoking `hidparse()` for collections and input items. `hidparse()` collects keyboard/consumer usages, button states, relative pointer deltas, absolute X/Y coordinates scaled to 31-bit mouse coordinates, scroll deltas, contact ids, touch in-range/tip state, stylus buttons, and contact dimensions into `Hidreport`/`Hidslot` structures.

`readerproc()` reads reports in a high-priority process. Keyboard state is diffed against the previous key set to emit key-up/key-down scan codes, and a repeat process generates repeated scan codes after configurable delay/period. Pointer slots are matched by usage/id, absolute z is converted to relative movement, multiple slots are combined, button bits are mapped to Plan 9 mouse buttons, and either absolute (`a`) or relative (`m`) mouse messages are written.

The 9P control file supports reading current repeat settings, writing `repeat N`, `delay N`, `debug N`, entering `rawon`, and then sending raw HID output reports until `rawoff`. `threadmain()` scans all interrupt IN endpoints with keyboard/pointer/HID CSPs, starts one reader per endpoint, and posts the control service if any setup succeeds.
