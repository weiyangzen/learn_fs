# File Research: sources/os/plan9/9front/sys/src/9/bcm/emmc.c

BCM Arasan eMMC/SD host controller driver implementing Plan 9 `SDio`.

Key behavior:
- Defines controller registers and command/status/interrupt bits.
- Initializes/reset host controller and determines external clock rate from firmware clock API or default.
- Sets SD bus width and clock speed.
- Enables interrupts and handles card/data completion wakeups.
- Sends SD commands with response decoding and error recovery for command/data inhibit states.
- Uses DMA channel `DmaChanEmmc` for data transfers to/from the FIFO register.
- Integrates LED activity with `okay`.
- Registers itself with `addmmcio`.

Dependencies:
- Uses `getclkrate`, GPIO/interrupt helpers, DMA, cache flush via DMA, and generic SD layer.

Research notes:
- Transfer path is interrupt-assisted after DMA completion, then waits for `Datadone`.
