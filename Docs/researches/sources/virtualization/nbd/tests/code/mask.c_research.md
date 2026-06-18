# File Research: sources/virtualization/nbd/tests/code/mask.c

## Purpose
Tests `getmaskbyte()` for prefix lengths 0 through 8.

## Behavior
Calls `count_assert()` for expected byte masks: `0`, `0x80`, `0xC0`, `0xE0`, `0xF0`, `0xF8`, `0xFC`, `0xFE`, and `0xFF`.

## Dependencies
Uses `nbdsrv.h` and `macro.h`.

## Risks and Notes
Only covers the 0-8 range; larger inputs are expected by implementation to return `0xFF`.
