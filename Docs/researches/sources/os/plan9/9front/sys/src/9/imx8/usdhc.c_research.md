# File Research: sources/os/plan9/9front/sys/src/9/imx8/usdhc.c

Implements the i.MX8 USDHC SD/MMC host-controller backend for Plan 9’s `SDio` interface. It defines controller register offsets, bit fields, ADMA2 descriptors, a per-controller `Ctlr`, and two concrete controllers: `usdhc1` and `usdhc2`.

Key responsibilities:
- Initializes pad muxing, GPIO reset, clocks, and controller reset for USDHC1/USDHC2.
- Programs bus width and SD clock rate through `usdhcbus()` and `usdhcclk()`.
- Issues SD/MMC commands through `usdhccmd()`, including response decoding and command/data inhibit recovery.
- Sets up ADMA2 transfers in `usdhciosetup()` and waits for completion in `usdhcio()`.
- Registers interrupt handling with `intrenable()` and wakes blocked data I/O through a `Rendez`.

Important implementation details:
- ADMA descriptors are allocated with `sdmalloc()`, filled in `Maxdma` chunks, and written back with `cachedwbse()`.
- Data buffers must be 4-byte aligned, length must be 4-byte aligned, and block size is asserted <= 2048.
- Multi-block data commands use `Autocmd12`; explicit `STOP_TRANSMISSION` is ignored because hardware handles stop.
- Read buffers are writeback-invalidated before DMA and invalidated after successful DMA completion.
- `nomultiwrite = 1` is set on both registered `SDio` instances.

Dependencies and integration:
- Uses architecture services from i.MX8 support: `iomuxpad`, `gpioout`, `setclkgate`, `setclkrate`, `getclkrate`.
- Uses Plan 9 kernel primitives: `Rendez`, `sleep`, `wakeup`, `error(Eio)`, cache maintenance, physical address conversion.
- Exposes itself through `usdhclink()` via `addmmcio()`.

Research notes:
- This file is storage-controller code, not part of the IP stack.
- The driver is tightly coupled to fixed physical MMIO addresses under `VIRTIO`.
- Error paths reset command/data circuits when inhibit bits stick, which is important for recovery from failed card commands.
