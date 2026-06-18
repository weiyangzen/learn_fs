# File Research: sources/virtualization/nvme-cli/libnvme/test/ioctl/discovery.c

## Purpose
Mock tests for NVMe-oF discovery log retrieval.

## Test Coverage
Covers empty discovery logs, four-entry single fetch, five-entry multi-fetch chunking, generation-counter changes requiring refetch, max retry exhaustion, and errors during initial header fetch, entries fetch, and generation-counter verification.

## Behavior
Uses `libnvmf_discovery_args` with configurable max retries, calls `libnvmf_get_discovery_log()`, and validates returned headers/entries. Fixture helpers create valid printable ASCII fields and account for space-padded log strings.

## Relevance
Validates consistency and retry behavior for fabrics discovery log reads, which are central to NVMe-oF target enumeration.
