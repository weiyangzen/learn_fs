# File Research: sources/virtualization/nvme-cli/util/sighdl.h

## Role

`sighdl.h` declares shared signal state and installation functions for platform-specific implementations.

## API

- Includes `<stdbool.h>` and `<signal.h>`.
- Declares `extern volatile sig_atomic_t nvme_sigint_received`.
- Declares `extern volatile sig_atomic_t nvme_sigwinch_received`.
- Declares `nvme_install_sigint_handler()`.
- Declares `nvme_install_sigwinch_handler()`.

## Research Notes

The header exposes signal flags as globals rather than hiding them behind accessors. Linux defines both globals; Windows defines only the SIGINT global and returns `-ENOTSUP` for SIGWINCH installation, so cross-platform callers must respect the Meson-selected feature set.
