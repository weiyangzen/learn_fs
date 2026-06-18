# File Research: sources/virtualization/spdk/lib/ioat/ioat.c

`ioat.c` implements SPDK’s Intel I/OAT DMA engine library. It handles PCI enumeration/attach/detach, BAR mapping, channel reset/start, descriptor ring setup, copy/fill descriptor building, flush/doorbell submission, and completion polling.

Global driver state consists of a mutex and a TAILQ of attached channels. `spdk_ioat_probe()` enumerates PCI I/OAT devices under the lock, skips devices already attached, calls the user probe callback, attaches accepted devices, inserts them into the attached list, and calls the attach callback.

Attach enables PCI bus mastering, maps BAR0 register space, checks I/OAT version, reads DMA capabilities and max transfer size, allocates a DMA completion-update location, allocates a default 32K-entry software descriptor ring and DMA hardware descriptor ring, translates every hardware descriptor address, links descriptors into a ring, resets hardware, programs completion and chain addresses, submits a null descriptor, flushes, and waits for idle state.

Descriptor preparation supports null, copy, and fill descriptors. Build APIs split operations by physical contiguity and `max_xfer_size`, append descriptors to the ring, and attach the user callback only to the final descriptor of the logical operation. If the ring runs out of descriptors, the build path restores the original head so partially prepared descriptors are discarded. Submit APIs call build then `spdk_ioat_flush()`.

`spdk_ioat_flush()` marks the last descriptor for completion update and writes the descriptor count register. Completion polling reads the DMA completion-update memory, detects halted channels, walks completed descriptors from tail until the hardware-completed physical address is reached, invokes descriptor callbacks, advances tail, records `last_seen`, and returns the number of events.

Detach removes the channel from the global attached list under lock, unmaps BAR0, frees software and DMA rings, frees the completion-update buffer, and frees the channel.

Research notes: critical correctness areas are descriptor ring wraparound, physical address translation, head rollback on build failure, and hardware reset/start sequencing. Fill support depends on the device BFILL capability bit.
