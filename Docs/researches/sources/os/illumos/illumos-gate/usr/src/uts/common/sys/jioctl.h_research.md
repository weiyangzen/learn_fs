# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/jioctl.h

## Role

`jioctl.h` preserves low-level ioctl and packet constants for communication with historical windowing terminals and the `xt` driver. It documents the Jerq/Blit/5620/615/620/630 lineage and defines host-to-terminal and terminal-to-host control message layouts.

## Major Definitions

The `JTYPE` ioctl namespace is `('j' << 8)`. Defined requests include booting a window download, returning to default terminal emulation, querying layers, querying window size, setting millisecond timeouts, booting with debugger wait, bidirectional agent control, running layers, and setting xt protocol type.

`struct jwinsize` reports window dimensions in characters and pixels. `struct jerqmesg` carries a control command and channel. Terminal-to-host control codes describe data delivery, layer creation/deletion/reshape, unblock/exit/defunct/run events, and flow-control toggles. `struct bagent` carries source/destination byte-string pointers plus size for `JAGENT`.

## Interfaces

There are no function prototypes. The header exports ioctl numbers and control packet layouts used by terminal/xt consumers.

## Integration Notes

This is compatibility infrastructure for old terminal protocols. The pointer-bearing `struct bagent` is ABI-sensitive and architecture-sensitive; any ioctl handler must account for user/kernel pointer copying and possible 32-bit compatibility if still reachable.
