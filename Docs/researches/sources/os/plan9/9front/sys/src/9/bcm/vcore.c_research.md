# File Research: sources/os/plan9/9front/sys/src/9/bcm/vcore.c

VideoCore mailbox/property interface and BCM board service helpers.

Key responsibilities:
- Sends/receives mailbox messages through `MAILBOX` registers.
- Builds property-tag requests in the shared mailbox buffer.
- Initializes framebuffer geometry and returns framebuffer address/stride/depth.
- Controls framebuffer blanking and device power state.
- Queries Ethernet MAC, board revision, firmware revision, RAM size, clock rates, and CPU temperature.
- Sets clock rates and controls virtual/external GPIO-style LEDs.
- Provides xHCI reset helper.

Important behavior:
- Serializes property calls through a lock.
- Uses `VCBUFFER` for mailbox payloads.
- Converts mailbox responses into Plan 9 configuration structures.

Dependencies:
- BCM mailbox hardware, SoC clock/device IDs, GPIO helpers, cache-coherent mailbox memory, and framebuffer code.
