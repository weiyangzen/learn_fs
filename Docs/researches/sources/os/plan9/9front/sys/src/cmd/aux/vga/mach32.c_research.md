# File Research: sources/os/plan9/9front/sys/src/cmd/aux/vga/mach32.c

Implements older ATI Mach32 VGA-mode setup without accelerator support. It accesses ATI extended registers through index port `0x1CE`, unlocks multiple protection bits, saves selected extended and coprocessor registers, and derives memory size from the miscellaneous register.

`init` selects one of a small common fixed-clock table, configures 8-bit linear-style VGA register state, sets clock index bits, handles interlace, and disables the 128 KB CPU aperture bit to keep a 64 KB VGA aperture.

Notable issue: `atixinit` calls `alloc(sizeof(mach32))` where `mach32` is a pointer variable, underallocating the `Mach32` structure that `snarf` later fills. `load` disables linear/memory-boundary state and writes selected extended registers.
