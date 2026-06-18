# File Research: sources/virtualization/nvme-cli/util/sighdl-win.c

## Role

`sighdl-win.c` is the Windows signal-handling implementation selected by Meson when `host_system == 'windows'`.

## Behavior

- Defines `volatile sig_atomic_t nvme_sigint_received`.
- Installs a `SIGINT` handler using standard C `signal()`.
- Resets the flag before installation and returns `-errno` if `signal()` returns `SIG_ERR`.
- `nvme_install_sigwinch_handler()` returns `-ENOTSUP`, reflecting that terminal resize handling via SIGWINCH is unsupported in this Windows implementation.

## Notable Detail

Unlike `sighdl.h`, this file does not define `nvme_sigwinch_received`. That is acceptable only if Windows-linked objects do not reference the global. Meson excludes `dashboard.c` on Windows, which is the primary consumer of SIGWINCH state in this group.

## Research Notes

The Windows implementation is intentionally narrower than the Linux one. It supports interrupt detection but not dashboard-style resize events.
