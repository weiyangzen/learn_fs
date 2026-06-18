# File Research: sources/os/plan9/9front/sys/src/9/imx8/sai.c

Role: i.MX8 SAI2 transmit-only audio driver for Plan 9 audio output with ring buffering and headphone sense.

Key responsibilities:
- Defines SAI transmit registers/control bits and a software ring buffer.
- Tracks buffered/available bytes in a circular buffer with one sample-sized gap.
- `saiwrite()` copies user audio into the ring, starts hardware when enough delay-buffered data exists, and sleeps for room/output pacing.
- `saireset()` resets FIFO/software state and configures I2S-style 16-bit packed stereo transmit framing.
- `fifo()` drains ring data into the SAI transmit FIFO in 32-bit words.
- Interrupt handler responds to FIFO error/request/warn, stops on underrun, fills FIFO, acknowledges, and wakes writers.
- Exposes audio control command `reset`, status reporting, buffered count, close behavior, and card probe.
- `saiprobe()` allocates controller/ring state, configures SAI2 pads, gates clock, registers IRQ, configures headphone-detect GPIO interrupt, and registers audio callbacks.
- `sailink()` registers the card type `sai`.

Dependencies:
- Plan 9 audio interface, GPIO, IOMUX, CCM, GIC.

Notes:
- Only controller 0 is accepted.
- Ring size is `44100 * 4 * 2` bytes.
- Headphone sense is sampled from `GPIO_PIN(4, 21)` and stored as `hp`.
