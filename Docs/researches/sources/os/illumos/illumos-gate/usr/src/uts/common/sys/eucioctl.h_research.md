# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/eucioctl.h

## Role

`eucioctl.h` defines ioctl commands and small payloads for passing EUC width and mode state to line-discipline STREAMS modules.

## Ioctl Contract

- Defines `EUC_IOC` and ioctl commands `EUC_WSET`, `EUC_WGET`, `EUC_MSAVE`, `EUC_MREST`, `EUC_IXLOFF`, `EUC_IXLON`, `EUC_OXLOFF`, and `EUC_OXLON`.
- Defines compact `struct eucioc`/`eucioc_t` containing four EUC byte widths and four screen widths as unsigned chars. The comments explain this intentionally differs from `eucwidth_t` to keep downstream messages small.
- Defines `EUC_BCAST` for line-discipline broadcast messages and one-byte broadcast states `EUC_B_CANON` and nonzero `EUC_B_RAW`.

## STREAMS Notes

The broadcast protocol is an `M_CTL` message with an `iocblk` containing `EUC_BCAST`, followed by an `M_DATA` block carrying raw/canonical state.
