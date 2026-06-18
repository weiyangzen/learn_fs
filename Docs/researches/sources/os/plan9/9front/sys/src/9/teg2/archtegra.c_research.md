# File Research: sources/os/plan9/9front/sys/src/9/teg2/archtegra.c

Tegra 2 SoC support file. It defines MMIO register layouts for clock/reset, power, SCU, flow controller, diagnostics, and the global `soc` address table for core devices.

Responsibilities include CPU clock defaults and errata setup, Ethernet device declaration (`rtl8169` on PCIe), SCU enablement, available CPU count, clock/reset enablement, stopping/starting secondary CPUs, SMP/cache-coherency diagnostics, secure-mode checks, Cortex-A9 auxiliary control setup, secondary CPU entry (`cpustart`), SGI interrupt handling, board reset/reboot, device accessibility checks, and flash stubs.

Important coupling: secondary CPUs wait on `l1ptstable`, which the RTL8169 attach path sets after PCI/Ethernet init stabilizes the L1 page table.
