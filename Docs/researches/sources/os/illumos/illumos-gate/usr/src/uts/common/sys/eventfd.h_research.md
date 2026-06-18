# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/eventfd.h

## Role

`eventfd.h` defines illumos support for Linux-compatible `eventfd`. It fixes flag values to Linux ABI values and declares the userland helpers.

## Definitions

- Defines `eventfd_t` as `uint64_t`.
- Defines Linux-compatible flags `EFD_CLOEXEC`, `EFD_NONBLOCK`, and `EFD_SEMAPHORE`.
- Defines native-private ioctl base `EVENTFDIOC` and `EVENTFDIOC_SEMAPHORE`, used to toggle semaphore mode internally.
- Userland declarations are `eventfd()`, `eventfd_read()`, and `eventfd_write()`.
- Kernel-only definitions include minor node constants `EVENTFDMNRN_EVENTFD`, `EVENTFDMNRN_CLONE`, and max counter value `EVENTFD_VALMAX` as `ULLONG_MAX - 1`.
