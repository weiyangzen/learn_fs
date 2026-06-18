# File Research: sources/virtualization/spdk/module/accel/dpdk_cryptodev/accel_dpdk_cryptodev_rpc.c

## Purpose

Defines RPCs for enabling and selecting/querying the DPDK cryptodev accel driver.

## Key RPCs

- `dpdk_cryptodev_scan_accel_module`
  - startup only
  - rejects params
  - calls `accel_dpdk_cryptodev_enable()`
- `dpdk_cryptodev_set_driver`
  - startup only
  - decodes `driver_name`
  - calls `accel_dpdk_cryptodev_set_driver()`
- `dpdk_cryptodev_get_driver`
  - startup and runtime
  - rejects params
  - returns current driver string

## Relationships

- Uses generated RPC decode helpers from `spdk_internal/rpc_autogen.h`.
- Uses conversion/accessor functions from `accel_dpdk_cryptodev.h`.
