# File Research: sources/os/plan9/9front/sys/src/9/pc/pmmc.c

Implements a PCI SD/MMC host-controller driver through the Plan 9 `SDio` interface. It targets SDHCI-like controllers and includes Ricoh-specific support.

Key behavior:
- Defines SD host-controller register offsets, normal interrupt bits, error interrupt bits, present-state bits, transfer-mode bits, and command-response encodings.
- `pmmcinit()` scans PCI devices for class `08/05` SD host controllers or Ricoh 5U822/5U823 devices, maps MMIO BAR0 with `vmap()`, enables the PCI device, and applies Ricoh SD2.0/base-clock quirks.
- `mmcinterrupt()` acknowledges normal/error interrupts, records card insertion/removal, accumulates wait status, and wakes sleepers.
- `resetctlr()` disables interrupts, resets the controller, sets timeout, enables interrupt masks, powers the card, and starts a 400 kHz clock.
- `pmmccmd()` builds SD command register fields, handles response types, checks card presence and command/data inhibit bits, writes command/argument/mode registers, waits for completion, and extracts 48-bit/136-bit responses.
- `pmmciosetup()` records block size/count; `pmmcio()` transfers data using PIO through `Rdat0`.
- `pmmcbus()` switches 1-bit/4-bit width and adjusts clock rate.
- `pmmclink()` registers the driver with `addmmcio()`.

Research notes:
- The driver uses PIO, not SDMA/ADMA, despite exposing DMA-related registers.
- Timeout/error paths reset command/data lines through `softreset(c, 0)`.
- Filesystem relevance is via block-device access for SD/MMC media.
