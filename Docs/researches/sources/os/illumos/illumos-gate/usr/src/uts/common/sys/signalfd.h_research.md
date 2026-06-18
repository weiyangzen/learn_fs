# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/signalfd.h

## Role

Defines illumos support for Linux-compatible `signalfd`.

## Key Interfaces

- Linux-compatible flags:
  - `SFD_CLOEXEC`
  - `SFD_NONBLOCK`
- Native private ioctl namespace:
  - `SIGNALFDIOC`
  - `SIGNALFDIOC_MASK`
- `signalfd_siginfo_t` is a 128-byte Linux-compatible signal-info record with signal number, errno, code, sender PID/UID, fd, band, trap, status, CPU times, address, and reserved padding.
- Userland declares `signalfd()`.
- Kernel minor names distinguish signalfd and clone devices.
- Kernel `sigfd_proc_state_t`, protected by `p_lock`, stores poll wake callback and a list of signalfd state.
- Exports kernel hook `sigfd_exit_helper`.

## Risk Notes

The header explicitly targets Linux binary compatibility for flags and struct size. Extending fields independently of Linux would break that contract.
