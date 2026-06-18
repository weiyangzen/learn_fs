# File Research: sources/os/plan9/9front/sys/src/9/pc/audiosb16.c

ISA Sound Blaster 16 and ESS1688-compatible playback driver.

Key responsibilities:
- Probes configured ISA audio devices, initializes SB16 or ESS1688-compatible hardware, allocates DMA buffers, and registers audio cards.
- Implements mixer controls for master, audio, synth, CD, line, mic, speaker, bass/treble, record/output gain, speed, and delay.
- Provides write-side playback using a circular buffer backed by looped DMA.
- Handles SB16 and ESS1688 command/status protocols, reset sequences, interrupt acknowledgement, and DMA continuation/stop.
- Registers interrupt handlers and audio status/buffered callbacks.

Important behavior:
- Uses 4 KiB transfer blocks inside a 64 KiB ring.
- SB16 playback programs signed 16-bit stereo autoinit DMA; ESS1688 has separate extended-register setup.
- Playback starts when data is available and stops at end of count when less than one block remains buffered.
- The driver registers both `sb16` and `ess1688` card names.

Dependencies:
- Depends on ISA configuration, low DMA helpers, I/O port allocation, interrupt registration, and generic audio volume helpers.

Notable risks:
- The read/capture paths are mostly dormant; the operational path is playback-oriented.
- Port/IRQ/DMA probing is constrained to classic ISA ranges and may mark failed cards as permanently unavailable.
