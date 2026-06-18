# File Research: sources/os/plan9/plan9/sys/src/9/teg2/archtegra.c

NVIDIA Tegra 2 board and Cortex-A9 MPCore support for Plan 9. It defines SoC register maps, CPU/cache/clock reset setup, SMP bring-up, Ethernet selection, reset/reboot, and device-presence checks.

Key responsibilities:
- Defines typed register layouts for clock/reset, power, SCU, flow controller, and cache-coherency diagnostics.
- Populates global `soc` physical/MMIO addresses for clocks, power, exception-vector handoff, SCU/GIC, UARTs, timers, PCIe, Ethernet, flash, EHCI, IDE, GPIO, SPI, I2C, and MMC.
- Applies Cortex-A9 errata workarounds via CP15 diagnostic-register writes.
- Initializes CPU frequency/delay-loop estimates from defaults or `*cpumhz`.
- Selects the RTL8169 PCIe Ethernet controller for `archether`.
- Enables SCU, SMP/coherency bits, Cortex-A9 cache configuration, clocks, and software-generated interrupt handlers.
- Starts secondary CPUs through Tegra's undocumented exception-vector register, unfreezes flow/reset state, and waits for the secondary CPU to acknowledge.
- Handles secondary CPU startup, including traps/clocks/timers, L1 cache coherence diagnostics, waiting for RTL8169 initialization to stabilize L1 page tables, MMU initialization, FPU enable, and scheduler entry.
- Implements CPU stop, board reboot through clock/reset registers, keyboard stub, flash stubs, and register-access probes for required devices.

Important behavior:
- Secondary CPUs wait on `l1ptstable.word` because the 8169 initialization must finish before copying CPU0's L1 page table.
- `l1diag` is compiled but inactive unless `Debug` is set.
- `clockson` clears all reset bits and enables all clock outputs.

Dependencies and assumptions:
- Assumes a Cortex-A9 in secure mode; `cksecure` panics if running non-secure.
- Depends on CP15 helpers, cache maintenance, SCU/GIC support, MMU code, PCI, RTL8169, and Plan 9 SMP state.

Notable risks:
- CPU startup relies on an undocumented Tegra exception-vector register and comments acknowledge Linux-derived/experimental behavior.
- Flash reset is intentionally unfinished and panics if used.
- `stopcpu` and `startcpu` only cover the flow-controller CPU range available on Tegra 2.
