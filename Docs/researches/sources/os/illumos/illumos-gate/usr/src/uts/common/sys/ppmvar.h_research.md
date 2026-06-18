# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/ppmvar.h

## Purpose
Defines private platform power-management driver state for devices, domains, control methods, configuration database entries, locks, debug flags, and common driver hooks.

## Main Interfaces
- Driver/unit state:
  - `ppm_unit_t`
  - `PPM_STATE_SUSPENDED`
- Domain helpers and LED timing:
  - `PPM_DOMAIN_UP`
  - `PPM_LED_PULSE`, `PPM_LEDON_INTERVAL`, `PPM_LEDOFF_INTERVAL`
  - `PPM_LEDON`, `PPM_LEDOFF`
- Configuration/device/domain types:
  - `ppm_db_t`
  - `ppm_cdata`
  - `ppm_dev_t`
  - `ppm_owned_t`
  - `ppm_dc_t`
  - `ppm_domain_t`
  - `ppm_domit`
  - `ppm_funcs`
- Device flags:
  - `PPMDEV_PCI66_D2`
  - `PPMDEV_PCI_PROP_CLKPM`
  - `PPM_PM_POWEROP`
  - `PPM_PHC_WHILE_SET_POWER`
- Domain-control commands:
  - `PPMDC_CPU_NEXT`, `PPMDC_PRE_CHNG`, `PPMDC_CPU_GO`, `PPMDC_POST_CHNG`
  - `PPMDC_FET_ON`, `PPMDC_FET_OFF`, `PPMDC_LED_ON`, `PPMDC_LED_OFF`
  - clock, pre/post power, reset, and S3 enter/exit commands.
- Control methods:
  - `PPMDC_KIO`
  - `PPMDC_CPUSPEEDKIO`
  - `PPMDC_VCORE`
  - SPARC-only `PPMDC_I2CKIO`
- Domain models and flags:
  - `PPMD_CPU`, `PPMD_FET`, `PPMD_LED`, `PPMD_PCI`, `PPMD_PCI_PROP`, `PPMD_PCIE`, `PPMD_SX`
  - `PPMD_IS_PCI`
  - `PPMD_OFF`, `PPMD_ON`
  - `PPMD_LOCK_ONE`, `PPMD_LOCK_ALL`, PCI speed/init/offline/CPU-ready flags.
- Global state and hooks:
  - `ppm_domain_p`, `ppm_statep`, `ppm_inst`, `ppm_domains`, `ppmf`
  - `ppm_dev_init()`, `ppm_dev_fini()`, `ppm_create_db()`, `ppm_claim_dev()`, `ppm_rem_dev()`, `ppm_get_dev()`
  - lookup/layer/init/ownership/power-change helpers.
- Private-data and locking macros:
  - `PPM_GET_PRIVATE`
  - `PPM_SET_PRIVATE`
  - `PPM_LOCK_DOMAIN`
  - `PPM_UNLOCK_DOMAIN`
- Debug-only flags and `PPMD`/`DPRINTF`.

## Dependencies And Relationships
Includes `sys/epm.h` and `sys/sunldi.h`, and uses layered driver handles to issue control operations to platform control devices. It backs the ioctl ABI in `ppmio.h`.

## Research Notes
`ppm_dc_t` uses a method-selected union where the first fields of each substructure must remain ordered as `iord`, `iowr`, and `val`. Domain lock macros maintain a reference count while conditionally acquiring/releasing the mutex.
