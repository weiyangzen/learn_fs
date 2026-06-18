# File Research: sources/os/plan9/9front/sys/src/9/omap/archomap.c

OMAP3530/Cortex-A8 board support for the 9front `omap` kernel, aimed at BeagleBoard and IGEPv2-style boards. It defines memory-mapped register layouts and board setup for clocks, GPIO, pin muxing, USB host/TLL/OTG, display clocks, cache identification, VFP enablement, reboot, Ethernet defaults, and flash reset.

Key behavior:
- `archconfinit` chooses the CPU frequency, defaulting to 500 MHz unless `*cpumhz` is configured.
- `configclks` sequences MPU, USB, PLL, wakeup, peripheral, and core clocks, including DPLL setup and GPTIMER clock selection.
- `configgpio` programs GPIO6 pin 176 as the SMSC9221 Ethernet interrupt input.
- `configscreengpio` and `screenclockson` enable GPIO1/DSS pieces needed by the LCD/display path.
- `setpadmodes` writes SCM pad configuration for USB, UART3, IGEP Ethernet IRQ, and GPMC/flash pins.
- `resetusb` resets OTG, UHH, and USB TLL blocks and sets host/TLL operating modes.
- `fpon` enables ARM VFP/NEON coprocessor access and prints VFP identity/capability information.
- `archreset` performs early SoC initialization: cache report, software boot config cleanup, pin muxing, clocks, GPIO, memory config, USB reset, and FPU enablement.
- `archreboot` requests global software reset through PRM reset control and spins if reset does not happen.
- `archether` declares a board Ethernet controller of type `9221` on IRQ 34.
- `cacheinfo` reads CP15 cache size/type registers for the two Cortex-A8 cache levels.

Notable dependencies:
- OMAP physical addresses from `mem.h`.
- ARM CP15 and VFP definitions from `arm.h`.
- USB EHCI structures from `usbehci.h`.
- Network and flash interfaces from the port layer.

Research notes:
- The file contains many hard-coded board register values and comments documenting U-Boot-derived pad settings.
- L3 protection-region dumping exists for diagnostics; modification code is left disabled under `if(0)`.
- USB setup is explicit about OMAP3 quirks, including port/TLL/ULPI mode constraints.
