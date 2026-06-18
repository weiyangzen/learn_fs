# File Research: sources/os/plan9/9front/sys/src/9/zynq/emmc.c

Purpose: Zynq eMMC/SD host controller driver for the portable Plan 9 SDIO layer.

Key behavior:
- Maps SDIO controller, resets host, configures clock, enables interrupt.
- Implements SDIO callbacks: init, enable, inquiry, command, DMA setup, I/O completion, bus width/speed.
- `emmccmd` builds command-transfer mode bits from `SDiocmd`, handles command/data inhibit recovery, reads responses, and waits for busy completion.
- `emmciosetup` configures system DMA address and block count/size with cache clean.
- `emmcio` waits for data completion, checks errors, and invalidates caches after reads.
- `emmclink` registers the controller via `addmmcio`.

Integration notes: Depends on `../port/sd.h`, interrupt handling, cache maintenance helpers, and physical address conversion.

Risk/attention points: Uses timeout sleeps for data completion. DMA length is capped by controller limits and assumes buffers are physically addressable.
