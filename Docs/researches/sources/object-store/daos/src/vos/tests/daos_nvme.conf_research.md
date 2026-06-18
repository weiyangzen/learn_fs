# sources/object-store/daos/src/vos/tests/daos_nvme.conf

## Purpose
SPDK JSON configuration for VOS tests needing a simple NVMe/bdev backend. It configures bdev options and creates one AIO block device backed by `/tmp/aio_file`.

## Important APIs, types, and functions
- Top-level `subsystems` entry for `bdev`.
- `bdev_set_options` sets I/O pool/cache sizes.
- `bdev_nvme_set_options` sets retry, timeout, admin queue polling, and timeout action.
- `bdev_nvme_set_hotplug` disables hotplug.
- `bdev_aio_create` creates `AIO_1` with 4096-byte block size and `/tmp/aio_file`.

## Control flow
This is declarative JSON consumed by SPDK/DAOS initialization. Methods are applied by the bdev subsystem in listed order.

## State and persistence behavior
The config can cause `/tmp/aio_file` to be used as backing storage for an AIO bdev. It stores no runtime state itself. Tests using it may create or mutate that file.

## Dependencies and integration points
Integrates DAOS/VOS NVMe test startup with SPDK bdev RPC/config machinery. The AIO backend allows tests to run without a physical NVMe device.

## Risks and edge cases
The hard-coded `/tmp/aio_file` can collide between tests or stale runs. Timeout and hotplug settings are test-oriented and not production defaults. Missing SPDK AIO support or insufficient permissions will break consumers.

## Test signals
Signals include successful SPDK config load, creation of `AIO_1`, and VOS tests observing an NVMe-capable backend.
