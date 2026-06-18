# File Research: sources/os/plan9/plan9/sys/src/9/bcm/emmc.c

BCM2835 Arasan eMMC/SD host controller driver implementing Plan 9 `SDio`.

Key behavior:
- Defines eMMC register offsets and command/interrupt/status/control bits.
- `cmdinfo[]` maps supported MMC/SD command numbers to response/data/CRC/index flags.
- `emmcinit()` obtains external eMMC clock from VideoCore (`getclkrate(ClkEmmc)`), falls back to 100 MHz, and resets the host controller.
- `emmcenable()` starts with 400 kHz initialization clock, enables interrupts, and waits for clock stability.
- `emmccmd()` handles command inhibit/data inhibit recovery, sends commands, waits for completion, decodes 136/48/no responses, handles busy responses, switches to 25 MHz after card select, and updates host data width after `Setbuswidth`.
- `emmciosetup()` programs block size/count.
- `emmcio()` performs data transfers through DMA channel `DmaChanEmmc`, waits for DMA and `Datadone`, and reports timeouts/errors.
- `mmcinterrupt()` captures data/error interrupts and wakes sleepers.
- Exports `SDio sdio = { "emmc", ... }`.

This driver depends on `dma.c`, `vcore.c`, timer/delay functions, and shared `../port/sd.h`.
