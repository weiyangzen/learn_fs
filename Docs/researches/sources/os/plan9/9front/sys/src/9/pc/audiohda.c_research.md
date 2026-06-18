# File Research: sources/os/plan9/9front/sys/src/9/pc/audiohda.c

Intel High Definition Audio/Azalia PCI driver with codec graph discovery and stream DMA.

Key responsibilities:
- Matches HDA PCI controllers, maps MMIO registers, applies vendor-specific controller quirks, and starts CORB/RIRB command DMA.
- Enumerates codecs, audio function groups, widgets, connection lists, pin defaults, capabilities, and amplifier ranges.
- Selects default input/output pins, finds audio paths through widget graphs, mutes/disconnects old paths, and connects converter-to-pin routes.
- Allocates input and output DMA streams with buffer descriptor lists and circular audio buffers.
- Implements audio read/write/close/status/control operations and volume controls for output, record gain, speed, and delay.
- Handles stream interrupts, command response interrupts, buffer position updates, underrun/overrun stops, and wakeups.
- Exposes `#P/hdacmd` for raw HDA verb submission and response reading against the last initialized card.

Important behavior:
- Uses 256 blocks over a 256 KiB stream buffer and 16-bit stereo 44.1 kHz format by default.
- Supports explicit route syntax through `pin` and `inpin` control writes.
- Scores output pins by fixed/jack status, green color, rear/external location, and line/headphone function.
- Scores input pins mostly by fixed/jack status.
- Uses CORB/RIRB polling for commands but keeps RIRB interrupt handshakes for QEMU compatibility.

Dependencies:
- Depends on PCI, audio interface helpers, MMIO register access, interrupt routing, queues, and Plan 9 physical DMA address conversion.

Notable risks:
- Codec graph traversal and route strings are compact and assume sane widget connection data.
- `lastcard` means `#P/hdacmd` targets only the most recently initialized HDA controller.
- Some supported PCI IDs are marked untested, and several vendor workarounds use magic config-register writes.
