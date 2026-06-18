# File Research: sources/os/plan9/9front/sys/src/9/pc/audioac97.c

PCI AC'97 audio controller driver with bus-master DMA rings and mixer hookup.

Key responsibilities:
- Matches known AC'97 PCI audio controller IDs and supports I/O-port and MMIO register layouts.
- Allocates input, output, and microphone circular buffers plus 32 hardware descriptors per stream.
- Handles playback writes, capture reads, stream close padding, status reporting, and buffered byte accounting.
- Services controller interrupts by advancing ring positions from current descriptor indices and waking sleepers.
- Initializes AC-link reset, codec readiness, bus-master registers, DMA descriptors, and interrupt routing.
- Hooks `audioac97mix.c` through register read/write callbacks.

Important behavior:
- Uses 32 KiB rings split into 32 descriptors and 4-byte stereo samples.
- ICH4 through ICH7 can use memory BARs; older controllers use paired I/O BARs.
- SiS 7012 has special status-clear behavior and descriptor size handling.
- Playback throttles according to `adev->delay`.

Dependencies:
- Depends on PCI, Plan 9 audio interface, DMA-address macros, interrupt registration, I/O allocation, and AC'97 codec mixer helpers.

Notable risks:
- Device matching includes untested IDs.
- Ring indices are updated from hardware descriptor position and assume descriptor/block alignment.
- Codec access waits are bounded but failures only print diagnostics.
