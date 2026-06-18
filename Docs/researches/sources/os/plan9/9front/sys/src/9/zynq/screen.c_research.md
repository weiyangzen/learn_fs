# File Research: sources/os/plan9/9front/sys/src/9/zynq/screen.c

Purpose: Zynq software framebuffer bridge and hardware cursor/control integration for Plan 9 draw/mouse code.

Key behavior:
- Maintains `gscreen` as a `Memimage` backing screen.
- `flushmemscreen` coalesces dirty rectangles and wakes the framebuffer copy process.
- `attachscreen` exposes the software screen to draw.
- `fbctlwrite` handles framebuffer control commands: `addr`, `size`, `init`.
- `screenproc` copies dirty regions from `gscreen` into a user-provided framebuffer-mapped segment.
- `mousectl` handles cursor register address and acceleration mode.
- `cursorproc` writes hardware cursor bitmap and position registers.
- `fbctlread` reports current size/channel and framebuffer address.

Integration notes: `devarch.c` exposes `fbctl`; `screen.h` declares this file’s hooks for portable draw/mouse code.

Risk/attention points: Framebuffer and cursor MMIO addresses are supplied through user segments and validated for writability/range. Helper kprocs are killed/restarted when addresses change.
