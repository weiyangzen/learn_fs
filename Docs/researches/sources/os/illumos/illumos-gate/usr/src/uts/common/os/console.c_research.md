# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/os/console.c

This file implements common kernel console I/O helpers for early boot, panic, PROM fallback, and normal asynchronous `/dev/console` output.

Core behavior:
- Global state includes `console_vnode`, `console_taskq`, and the current polled I/O vector `cons_polledio`.
- `console_hold()`/`console_rele()` serialize direct console rendering with a writer rwlock, recursion depth, framebuffer power management, and optional framebuffer/specfs/devinfo lock checks.
- `console_enter()`/`console_exit()` are used around PROM rendering so platform code can stop other CPUs if framebuffer mappings are busy.
- `console_get_size()` reads screen rows/columns/pixel dimensions from terminal-emulator or root-node properties, clamps values to supported defaults/ranges, and handles pre-DDI fallback.
- `console_vprintf()` normally formats into a heap message and dispatches `console_putmsg()` on `console_taskq` when `/dev/console` is ready and the system is not panicking.
- `console_putmsg()` writes to `console_vnode` with `vn_rdwr(FAPPEND)`; if unavailable or failing, it falls back to PROM printing under console hold/enter protection.
- `console_printf()` wraps `console_vprintf()`.
- `console_puts()` writes a byte string directly through PROM and is intended only for the wscons driver legacy path.
- `console_putc()` writes one character directly to PROM, expanding newline to carriage-return/newline.
- `console_gets()` and `console_getc()` read from PROM only during early boot before `rconsvp` is initialized; `console_gets()` handles erase, kill-line, newline, and buffer-full bell behavior.

Important invariants:
- Panic paths assume exclusive access and avoid changing console lock state.
- Recursive console holds increment `console_depth` and release only at the outermost exit.
- Firmware framebuffer locking is conditional on firmware console mode, multiprocessor systems, and framebuffer vnode availability.
- Asynchronous console taskq output is skipped during panic or when allocation/dispatch fails.
- Synchronous console input is asserted to occur only before the real console stream exists.
