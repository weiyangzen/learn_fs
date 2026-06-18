# File Research: sources/virtualization/spdk/app/fio/bdev/bdev_zoned.json

## Purpose
SPDK JSON configuration for exercising fio against a zoned bdev stack.

## Main Contents
- Creates malloc bdev `Malloc0` with `2097152` blocks of size `512`.
- Creates zone block bdev `Zone0` on top of `Malloc0`.
- Sets `zone_capacity` to `262144`.
- Sets `optimal_open_zones` to `8`.

## Dependencies
Uses SPDK bdev RPC methods `bdev_malloc_create` and `bdev_zone_block_create`.

## Filesystem/Block Relevance
Provides a host-managed zoned block target for fio ZBD testing through the SPDK bdev fio plugin.

## Risks and Notes
- The zoned behavior is layered over volatile malloc storage.
- Zone geometry is static and intentionally small enough for local tests.
