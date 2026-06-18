# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/pcie_pwr.h

## Purpose
Defines PCIe nexus power-management state, child power counters, PM capability/flag bits, PPM ioctl request IDs, and common PCIe power-management helper prototypes shared by multiple PCIe-related drivers.

## Main Interfaces
- Counter indexes and count:
  - `PCIE_D3_INDEX`
  - `PCIE_D2_INDEX`
  - `PCIE_D1_INDEX`
  - `PCIE_D0_INDEX`
  - `PCIE_UNKNOWN_INDEX`
  - `PCIE_MAX_PWR_LEVELS`
- PM structures:
  - `pcie_pwr_t`: nexus PM state, lock, PM capability offset/handle, link/function levels, flags, hold count, and child-level counters.
  - `pcie_pwr_child_t`: per-child component counters.
  - `pcie_pm_t`: nexus and parent PM-info wrapper.
- PM-info macros:
  - `PCIE_PMINFO()`
  - `PCIE_NEXUS_PMINFO()`
  - `PCIE_PAR_PMINFO()`
  - `PCIE_CHILD_COUNTERS()`
  - `PCIE_SET_PMINFO()`
  - `PCIE_RESET_PMINFO()`
  - `PCIE_IS_COMPS_COUNTED()`
- Capability bits and helpers:
  - `PCIE_SUPPORTS_D3`
  - `PCIE_SUPPORTS_D2`
  - `PCIE_SUPPORTS_D1`
  - `PCIE_SUPPORTS_D0`
  - `PCIE_L2_CAP`
  - `PCIE_L0s_L1_CAP`
  - `PCIE_DEFAULT_LEVEL_SUPPORTED`
  - `PCIE_LEVEL_SUPPORTED()`
  - `PCIE_SUPPORTS_DEVICE_PM()`
- PM flags:
  - `PCIE_ASPM_ENABLED`
  - `PCIE_SLOT_LOADED`
  - `PCIE_PM_BUSY`
  - `PCIE_NO_CHILD_PM`
- Link PM levels:
  - `PM_LEVEL_L3`
  - `PM_LEVEL_L2`
  - `PM_LEVEL_L1`
  - `PM_LEVEL_L0`
- PPM requests:
  - `PPMREQ`
  - `PPMREQ_PRE_PWR_OFF`
  - `PPMREQ_PRE_PWR_ON`
  - `PPMREQ_POST_PWR_ON`
- Settle time:
  - `PCI_CLK_SETTLE_TIME`
- Power helper prototypes:
  - `pcie_plat_pwr_setup()`
  - `pcie_plat_pwr_teardown()`
  - `pwr_common_setup()`
  - `pwr_common_teardown()`
  - `pcie_bus_power()`
  - `pcie_power()`
  - `pcie_pm_add_child()`
  - `pcie_pm_remove_child()`
  - `pcie_pwr_suspend()`
  - `pcie_pwr_resume()`
  - `pcie_pm_hold()`
  - `pcie_pm_release()`

## Dependencies And Relationships
Uses PM level constants, DDI devinfo internals, PM bus power op types, mutexes, and access handles from includers. The object file is linked into multiple drivers, so lint-only symbol renaming avoids duplicate global warnings.

## Research Notes
The nexus tracks aggregate child power levels with counters, including an unknown bucket. `pcie_pm_hold()`/`pcie_pm_release()` provide a temporary busy hold around operations that should not race power-down.
