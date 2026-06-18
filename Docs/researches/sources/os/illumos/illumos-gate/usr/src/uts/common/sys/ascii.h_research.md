# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/ascii.h

## Purpose

`ascii.h` defines symbolic constants for ASCII control characters.

## Constants

The header maps names such as `A_NUL`, `A_SOH`, `A_STX`, `A_ETX`, `A_EOT`, `A_ENQ`, `A_ACK`, `A_BEL`, `A_BS`, `A_HT`, `A_NL`, `A_LF`, `A_VT`, `A_FF`, `A_NP`, `A_CR`, `A_ESC`, file/group/record/unit separators, and `A_DEL` to their byte values. It also defines `A_CSI` as `0x9b`.

## Research Notes

This is a utility constants header with no logic. It is included by terminal, console, serial, or parser code that prefers named control character constants over literals.
