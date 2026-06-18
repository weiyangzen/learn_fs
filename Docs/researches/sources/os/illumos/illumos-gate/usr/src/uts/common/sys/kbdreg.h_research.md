# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/kbdreg.h

## Role

`kbdreg.h` contains private keyboard implementation state shared by the keyboard translation implementation. It is not a public ioctl or user ABI header.

## Major Definitions

`struct keyboardstate` stores the current keyboard ID, ID-recognition state, scanner state, repeat key, bucky bits, shift mask, current keyboard table pointer, and toggle-shift mask. The ID recognizer states are `KID_NONE`, `KID_GOT_PREFACE`, `KID_OK`, and `KID_GOT_LAYOUT`.

## Interfaces

There are no function prototypes. Consumers use the state structure and recognizer constants internally.

## Integration Notes

This header depends on the keyboard table types from `kbd.h` and describes mutable translation/scanner state. It should remain private to keyboard implementation code because exposing or changing it affects scanner state-machine behavior and keyboard layout detection.
