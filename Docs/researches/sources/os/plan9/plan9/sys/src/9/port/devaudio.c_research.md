# File Research: sources/os/plan9/plan9/sys/src/9/port/devaudio.c

This file implements a Sound Blaster 16 / ESS1688 audio device exposed as Plan 9 files.

Key responsibilities:
- Exposes `audio`, `volume`, and `audiostat` files under device character `A`.
- Initializes SB16/ESS1688 hardware from ISA configuration, allocates I/O ports, sets IRQ/DMA, resets the DSP, and configures mixer state.
- Manages fixed DMA buffers through empty/full queues.
- Handles playback and recording using autoinit DMA.
- Handles SB16 and ESS1688 interrupt paths.
- Implements text-based volume control parsing and status reporting.
- Provides `audioread`, `audiowrite`, open/close logic, and optional byte swapping.

Filesystem/storage relevance:
- Not a filesystem/storage driver, but it is a representative Plan 9 synthetic device using `Dev`, `Chan`, directory entries, `Block` wrappers, and namespace exposure.
