# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/gpio/kgpio_provider.h

## Role

`kgpio_provider.h` defines the private kernel interface between the GPIO framework and GPIO provider drivers.

## Key Interfaces and Data

- Kernel-only provider callbacks:
  - name-to-ID lookup
  - attribute get/set using nvlists
  - DPIO capability query
  - DPIO input read
  - DPIO output-state get
  - DPIO output set
- `kgpio_ops_t` groups these callbacks for registration.
- `kgpio_register()` and `kgpio_unregister()` attach/detach a provider to a `dev_info_t`.
- Helper functions `kgpio_nvl_attr_fill_u32()` and `kgpio_nvl_attr_fill_str()` fill attribute nvlists with metadata, possible values, and protection.

## Dependencies and Use

The header includes nvpair, DPIO, and KGPIO attribute definitions. The provider API is under `_KERNEL`; userland cannot see the registration contract.

## Research Notes

Provider drivers expose all configuration through nvlists rather than fixed per-device structures. The DPIO callbacks are optional capability-backed operations tied to GPIO IDs.
