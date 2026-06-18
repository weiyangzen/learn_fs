# File Research: sources/os/plan9/plan9/sys/src/9/bcm/vcore.c

VideoCore mailbox/property interface for BCM firmware services.

Key behavior:
- Implements raw mailbox read/write for property channel and framebuffer channel.
- `vcreq()` builds a property request in `VCBUFFER`, performs cache maintenance, sends bus/physical address through mailbox, handles old/new base address fallback, validates response, and copies returned data.
- Framebuffer helpers:
  - `fbdefault()` gets firmware display resolution/depth.
  - `fbinit()` asks firmware to allocate framebuffer, maps returned framebuffer memory at `FRAMEBUFFER` via `mmukmap()`, and clears it.
  - `fbblank()` sends blank/unblank requests.
- Power helpers `setpower()`/`getpower()` use property tags.
- `getethermac()` returns firmware MAC address as lowercase hex string.
- `getfirmware()` returns firmware revision.
- `getramsize()` fills ARM RAM base/limit from firmware.
- `getclkrate()` returns firmware clock rates.

This is the BCM port’s firmware API for display, clocks, power, MAC, RAM sizing, and firmware revision.
