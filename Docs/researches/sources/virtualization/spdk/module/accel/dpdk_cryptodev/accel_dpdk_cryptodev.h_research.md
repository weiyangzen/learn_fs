# File Research: sources/virtualization/spdk/module/accel/dpdk_cryptodev/accel_dpdk_cryptodev.h

## Purpose

Header for DPDK cryptodev accel module control and driver conversion.

## Key Contents

- Includes public module enum header `spdk/module/accel/dpdk_cryptodev.h`.
- Declares:
  - `void accel_dpdk_cryptodev_enable(void);`
  - `int accel_dpdk_cryptodev_set_driver(enum spdk_accel_dpdk_cryptodev_driver driver);`
  - `enum spdk_accel_dpdk_cryptodev_driver accel_dpdk_cryptodev_get_driver(void);`
  - `const char *accel_dpdk_cryptodev_driver_to_str(enum spdk_accel_dpdk_cryptodev_driver driver);`

## Relationships

- Used by implementation and RPC file.
