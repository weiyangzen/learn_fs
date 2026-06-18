# File Research: sources/virtualization/nvme-cli/libnvme/src/nvme/nvme-types.h

## Role

Umbrella public header for libnvme NVMe type definitions.

## Key Content

Includes the family of NVMe type headers:

- `nvme/nvme-types-base.h`
- `nvme/nvme-types-fabrics.h`
- `nvme/nvme-types-mi.h`
- `nvme/nvme-types-nvm.h`
- `nvme/nvme-types-zns.h`

## Dependencies

This header has no declarations of its own besides `#pragma once` and include directives.

## Research Notes

This is a convenience aggregation point. Consumers can include it when they need broad NVMe type coverage rather than individual command-set or transport headers.

## Filesystem/Storage Relevance

Indirect relevance: it centralizes access to NVMe storage type definitions used by tooling that interacts with block devices and NVMe-oF environments.
