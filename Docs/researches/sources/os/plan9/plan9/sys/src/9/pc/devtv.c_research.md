# File Research: sources/os/plan9/plan9/sys/src/9/pc/devtv.c

Read completely: 2194 lines.

This file implements a Plan 9 Brooktree Bt848/Bt878 TV capture driver exposed as `#V`.

Key behavior:
- Probes Bt848/Bt878 PCI devices.
- Detects board variants and tuners through I2C EEPROMs and GPIO state.
- Supports Miro, Miro Pro, and Hauppauge Bt878-style boards.
- Exposes per-card directories `tvN` with `video`, `audio`, `ctl`, and `regs`.
- Initializes Bt848 video capture registers for NTSC-sized `640x480` active frames.
- Builds Brooktree RISC DMA programs for packed RGB16 and planar YCbCr formats.
- Supports video capture into allocated frame buffers or direct VGA memory.
- Supports Bt878 audio capture with a separate RISC program and ring of audio blocks.
- Handles MSP3400 audio control, volume, mute, tuning, and audio-format status.
- Loads Hauppauge KFIR/Altera microcode from `hcwAMC.h`.

Important interfaces:
- Device name: `tv`, rune `'V'`.
- Control commands:
  - `vstart`
  - `vgastart`
  - `vstop`
  - `astart`
  - `astop`
  - `channel`
  - `colormode`
  - `volume`
  - `mute`
- Color modes: `RGB16`, `YCbCr422`, `YCbCr411`.

Key internal pieces:
- `tvinit()` performs PCI discovery, maps registers, detects board/tuner, initializes capture defaults, and enables interrupts.
- `tvinterrupt()` handles video and audio RISC interrupts, errors, and block/frame advancement.
- `riscpacked()`, `riscplanar411()`, `riscplanar422()`, and `riscaudio()` generate hardware DMA instruction streams.
- `frequency()` tunes channels via tuner I2C commands.
- `mspreset()`, `mspvolume()`, and `msptune()` operate the MSP audio chip through bit-banged I2C.
- `kfirinitialize()` loads and resets the Hauppauge KFIR path.

Research notes:
- `video` reads return the last DMA-completed frame.
- `audio` reads track a per-open block cursor through `c->aux`.
- `regs` dumps Bt848 and optional Bt878 register windows.
- Lifetimes for video and audio buffers are guarded by reference counts to prevent stop/free while reads are active.
