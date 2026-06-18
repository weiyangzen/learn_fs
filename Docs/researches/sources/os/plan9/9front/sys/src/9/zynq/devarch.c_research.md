# File Research: sources/os/plan9/9front/sys/src/9/zynq/devarch.c

Purpose: Zynq-specific `#P/arch` device exposing CPU temperature, FPGA programmable-logic configuration, and framebuffer control.

Key behavior:
- `xadcinit`, `xadcirq`, and `xadctimer` configure/read XADC temperature and trigger shutdown-like `scram` at extreme temperature.
- PL support maps an AXI physical segment, configures device-controller interrupts, waits for INIT/DONE, and streams bitstream data through DMA.
- Device files: `cputemp`, `pl`, `fbctl`.
- `archread` returns temperature, waits for PL done, or delegates to framebuffer control.
- `archwrite` programs PL or delegates framebuffer control.
- `archinit` unlocks SLCR and initializes XADC/PL.

Integration notes: Uses `slcr`, `vmap`, interrupt framework, Plan 9 dev helpers, physical segment registration, and screen framebuffer functions.

Risk/attention points: Temperature thresholds cause printed warnings and eventually call `scram`. PL write path requires 4-byte aligned, positive lengths.
