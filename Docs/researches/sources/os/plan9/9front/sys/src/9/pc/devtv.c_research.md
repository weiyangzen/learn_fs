# File Research: sources/os/plan9/9front/sys/src/9/pc/devtv.c

## Purpose
Plan 9 `#V` TV capture device driver for Brooktree Bt848/Bt878 TV tuner/capture cards, including Hauppauge-specific audio/KFIR support.

## Exposed Interface
- Device table: `tvdevtab`, device character `V`, name `tv`.
- Namespace layout:
  - `#V/tvN/video`: read current captured video frame.
  - `#V/tvN/audio`: read captured audio blocks when Bt878 audio is present.
  - `#V/tvN/ctl`: control commands.
  - `#V/tvN/regs`: dump Bt848/Bt878 MMIO registers.
- Control commands:
  - `vstart <nframes>`
  - `astart <input> <rate> <blocks> <blocksize>`
  - `astop`
  - `vgastart <physaddr> <stride>`
  - `vstop`
  - `channel <channel> <finetune>`
  - `colormode <RGB16|YCbCr422|YCbCr411>`
  - `volume <left> <right>`
  - `mute`

## Implementation Notes
- `tvinit()` scans PCI for Bt848/Bt878 variants, maps MMIO registers, detects boards via I2C EEPROM probes, configures tuner type, initializes capture geometry, interrupt masks, GPIO audio muxing, and optional Bt878 audio path.
- The file contains a register-layout struct `Bt848`, board/tuner tables, Hauppauge EEPROM tuner mapping, audio mux tables, and NTSC geometry constants.
- Video capture is programmed with Bt848 RISC DMA instruction streams:
  - `riscpacked()` for packed RGB16.
  - `riscplanar411()` for planar YCbCr 4:1:1.
  - `riscplanar422()` for planar YCbCr 4:2:2.
- `vstart()` allocates frame buffers and DMA programs, chains frame programs in a ring, and `vactivate()` starts capture.
- `vgastart()` captures directly into a caller-supplied physical framebuffer.
- `vstop()` stops RISC/FIFO/capture and frees frame buffers, refusing while readers hold `fref`.
- Audio capture uses `riscaudio()`, `astart()`, `astop()`, Bt878 audio DMA, and `aref` to prevent freeing buffers during reads.
- `tvinterrupt()` acknowledges video/audio interrupt bits, records last completed video frame, advances audio block counters, wakes audio readers, and resets DMA on selected error conditions.
- I2C support is split between Bt848 hardware I2C operations (`i2cread`, `i2cwrite`) and bit-banged helpers used for MSP3400 audio-chip access.
- MSP3400 support includes reset, register read/write, volume/mute, audio standard autodetection, and status text in `tv->ainfo`.
- Hauppauge KFIR/Altera support loads `hcwAMC` microcode through GPIO and initializes the encoder/control logic.

## Filesystem Relevance
This is a rich Plan 9 device namespace example. It maps a PCI multimedia capture card into files and text commands, showing how Plan 9 drivers expose streaming buffers, register dumps, and mutable control state via `read`/`write` on device files.

## Risks / Quirks
- Several paths use `assert()`/`panic()` on allocation or unsupported board states.
- Audio read logic has debug `print()` calls and unusual block-index arithmetic.
- Capture dimensions are hard-coded to NTSC active geometry.
- Only selected boards/tuners are supported; STB cards explicitly panic.
- The driver directly accepts a physical address for `vgastart`, so correctness depends on trusted privileged use.
