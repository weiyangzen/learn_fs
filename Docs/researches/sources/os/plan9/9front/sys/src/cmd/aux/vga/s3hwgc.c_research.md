# File Research: sources/os/plan9/9front/sys/src/cmd/aux/vga/s3hwgc.c

Hardware graphics cursor gatekeeping descriptors for S3/RAMDAC combinations.

Key behavior:
- `init` marks the controller initialized, returns immediately if global `cflag` is already set, and otherwise requires an active VGA controller with enhanced-mode capability and depth at least 8. If requirements are not met, it disables cursor use via `cflag`; if they are met, it requests enhanced mode through `resyncinit`.
- `load` marks loaded and verifies enhanced mode is actually active at load time, disabling cursor use through `cflag` if not.
- Exposes no-op descriptors for `bt485hwgc`, `rgb524hwgc`, `tvp3020hwgc`, and `tvp3026hwgc`.
- Exposes `s3hwgc` with the active `init`/`load` validation logic.

Notable dependencies:
- Global cursor-disable flag `cflag`, current controller `vga->ctlr`, enhanced-mode flags, and `resyncinit` from the VGA framework.

Research notes:
- This file does not program cursor shape, colors, or position; it only enforces prerequisites and provides controller names for configuration.
- The no-op descriptors likely let configuration files name RAMDAC-specific cursor controllers while actual cursor support is elsewhere or absent.
