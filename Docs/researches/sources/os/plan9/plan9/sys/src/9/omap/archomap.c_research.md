# File Research: sources/os/plan9/plan9/sys/src/9/omap/archomap.c

Implements OMAP3530/Beagle/IGEP board-specific reset, clocks, GPIO, USB, pad muxing, CPU/cache reporting, Ethernet/flash hooks, and reboot support.

Key points:
- Defines hardware register layouts for USB OTG/TLL, L3 protection regions/agents, clock-management modules, power/reset management, GPIO, SCM pad config, and control ID registers.
- `archconfinit()` sets default CPU speed to 500MHz and allows `*cpumhz` override between 100MHz and 3GHz.
- Provides L3 firewall reporting helpers (`dumpl3pr()`) and cache reporting (`cacheinfo()`, `prcachecfg()`).
- `archether()` declares controller 0 as an SMSC9221-compatible 100Mbps Ethernet device on IRQ 34.
- `configmpu()` adjusts DPLL1/MPU clock multiplier to desired CPU frequency, with max based on SKU.
- `configpll()`, `configper()`, `configwkup()`, `configusb()`, and `configcore()` turn on functional/interface clocks needed for timers, GPIO, USB host/TLL, PLL outputs, and peripherals.
- `configgpio()` configures GPIO6 pin 176 as the SMSC9221 interrupt source and clears outstanding GPIO IRQs; `gpioirqclr()` acknowledges it.
- `configscreengpio()` and `screenclockson()` enable GPIO/DSS clocks and pins for display output.
- `setpadmodes()` programs USB, UART3, Ethernet IRQ, and GPMC/flash pad muxing, largely matching u-boot magic values.
- `fpon()` enables CP10/CP11 access, turns on VFP, reports VFP implementation, and configures FPSCR.
- `resetusb()` resets OTG, UHH, and TLL blocks, chooses ULPI PHY mode, and handles absent TLL.
- `archreset()` is guarded by `beenhere`, initializes temporary CPU timing, clears errata-related boot config memory, configures pads/clocks/GPIO, refreshes config, resets USB, and enables FP.
- `archreboot()` requests global software reset through PRM and loops if reset fails.
- Provides no-op `kbdinit()`, `lastresortprint()`, `cpuidprint()`, `chkmissing()`, `archflashwp()`, and `archflashreset()` for OneNAND on IGEPv2.

Dependencies and interactions:
- Called during early platform boot by `main.c` in the OMAP tree.
- Clock code in `clock.c` assumes timer clock choices made here.
- `ether9221.c` depends on GPIO and pad setup.
- USB host drivers depend on clock/reset setup.
- Display code depends on screen GPIO/DSS clock functions.

Research relevance:
- Primary board-support file for OMAP3530, connecting SoC clocks, muxes, buses, USB, Ethernet, display, flash, and reset behavior.
