# File Research: sources/virtualization/spdk/app/fio/bdev/bdev.json

## Purpose
Minimal SPDK JSON configuration for the bdev fio plugin.

## Main Contents
- Defines a single `bdev` subsystem configuration item.
- Creates malloc bdev `Malloc0`.
- Uses block size `512`.
- Uses `262144` blocks.

## Dependencies
Consumed by SPDK JSON/RPC configuration loading, specifically the `bdev_malloc_create` method.

## Filesystem/Block Relevance
Provides an in-memory block target for fio benchmarking without physical storage.

## Risks and Notes
- Capacity is fixed by the JSON values.
- It is suitable for testing plugin plumbing and memory-backed I/O, not persistence.
