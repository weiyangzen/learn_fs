# File Research: sources/virtualization/nvme-cli/util/sighdl-linux.c

## Role

`sighdl-linux.c` implements Linux signal handlers used by nvme-cli utilities, especially the live dashboard.

## Behavior

- Defines global `volatile sig_atomic_t nvme_sigint_received`.
- Defines global `volatile sig_atomic_t nvme_sigwinch_received`.
- `nvme_sigint_handler()` sets the SIGINT flag to `true`.
- `nvme_sigwinch_handler()` sets the SIGWINCH flag to `true`.
- `nvme_install_sigint_handler()` installs a `sigaction()` handler for `SIGINT`, resets the flag to `false`, and returns `-errno` on failure.
- `nvme_install_sigwinch_handler()` installs a `sigaction()` handler for `SIGWINCH`, resets the flag to `false`, and returns `-errno` on failure.

The handlers perform only async-signal-safe flag writes.

## Dependencies

Includes `<signal.h>`, `<errno.h>`, `<stddef.h>`, and `sighdl.h`. It relies on `stdbool.h` being included by `sighdl.h` for `true`/`false`.

## Research Notes

This implementation is paired with `dashboard.c`, which checks these flags after `pselect()` returns `EINTR`. The signal handlers do not chain or preserve previous handlers.
