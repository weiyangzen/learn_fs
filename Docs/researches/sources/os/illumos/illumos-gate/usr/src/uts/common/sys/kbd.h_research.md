# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/kbd.h

## Role

`kbd.h` defines Sun/PC/USB keyboard type constants, keyboard event codes, translation modes, modifier-state masks, keyboard table structures, compose/floating-accent structures, and encoded keymap action values used by the keyboard translation layer.

## Major Definitions

The header keeps obsolete keyboard type and command macros for source compatibility while identifying supported keyboard types: Sun Type 3, Sun Type 4, USB, PC 101, and ASCII-terminal keyboard. It defines special device bytes such as idle, error, reset, layout-prefix, pressed, and released, plus Sun keyboard control commands for reset, bell, click, autotest, LED setting, and layout query.

Translation modes are `TR_NONE`, `TR_ASCII`, `TR_EVENT`, and `TR_UNTRANS_EVENT`. `BUILDKEY`, `STATEOF`, and `KEYOF` encode/decode raw key transitions. Modifier and "bucky" state definitions cover Meta/System, caps/shift/control masks, AltGraph, Alt, NumLock, right Alt, and the reserved `UPMASK`.

The keymap model uses `keymap_entry_t` and either fixed-size `struct keymap` arrays or variable-size table pointers under `KEYMAP_SIZE_VARIABLE`. `struct keyboard` groups normal, shifted, caps, altgraph, numlock, control, and key-up maps with idle masks, abort sequences, toggle-shift state, exception maps, and newer abort sequences. `struct exception_map` represents modifier-sensitive overrides not expressible as ordinary keymap entries. Compose and floating-accent structures map two-step input sequences to UTF-8 keymap entries.

Encoded keymap actions use `SPECIAL(h, l)` in the top byte. Classes include shift keys, bucky bits, funny actions (`NOP`, `OOPS`, `HOLE`, `RESET`, `ERROR`, `IDLE`, `COMPOSE`, `NONL`), floating accents, string keys with `KTAB_STRLEN`, function-key groups, and keypad keys.

## Interfaces

There are no function prototypes. This file defines the data and value contract consumed by keyboard drivers, `kbtrans`, ioctl handlers, and keymap tables.

## Integration Notes

This header is a compatibility and data-format hub. Existing keymap tables depend on exact special-action encodings and modifier bits. The comments explicitly reserve some mask values and explain that keyboard-specific modules can opt into variable keymap sizes, which is essential for USB keyboards with up to 255 key entries.
