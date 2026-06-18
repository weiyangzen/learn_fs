# File Research: sources/os/plan9/9front/sys/src/9/imx8/ccm.c

Role: i.MX8 clock-control module support: named input clocks, root clock slices, module gates, PLL programming, and public clock rate/gate APIs.

Key responsibilities:
- Defines input clock IDs/frequencies/names for ARM/GPU/VPU/DRAM/system/audio/video PLLs, oscillator refs, and external refs.
- Defines root clock IDs/names for CPU, buses, display, USB, PCIe, SAI, ENET, I2C, UART, PWM, GPT, MIPI, CSI, and HDMI domains.
- Provides a large `root_clk_input_mux` table mapping each root clock to its valid mux inputs.
- Provides a large `clocks[]` module table mapping named module clocks to root slices and optional CCGR gate numbers.
- Programs fractional PLLs by searching divider/fraction settings, bypassing while changing, waiting for lock, then unbypassing.
- Supports analog PLL monitor output via special `ccm_analog_pllout` handling.
- Reads and writes CCGR gate state and root target registers, preserving active gates during root-clock reconfiguration.
- Computes current root rates including disabled-state negative return convention.
- Chooses pre/post divider values that do not exceed requested frequency, then enables the source PLL when needed.
- Exposes `setclkgate()`, `setclkrate()`, and `getclkrate()` by string name.

Dependencies:
- Hard-wired CCM MMIO at `VIRTIO + 0x380000` and analog top at `VIRTIO + 0x360000`.
- Used by nearly every i.MX8 driver to gate clocks and set bus/peripheral/display/USB/PCIe rates.

Notes and risks:
- Unknown clock or input names panic, so driver string names must match tables exactly.
- IPG-derived roots are special-cased and may be disabled in target writes.
- Some table entries are duplicated or commented with uncertainty, for example USB root comments and duplicated ECSPI2/perfmon naming, but behavior is table-driven.
