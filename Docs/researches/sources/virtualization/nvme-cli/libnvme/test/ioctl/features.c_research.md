# File Research: sources/virtualization/nvme-cli/libnvme/test/ioctl/features.c

## Purpose
Large mock-ioctl test suite for NVMe Get Features and Set Features command initializer helpers.

## Test Coverage
Covers generic set/get features plus feature-specific helpers for arbitration, power management, LBA range, temperature threshold, error recovery, volatile write cache, number of queues, IRQ coalescing/config, write atomicity, async events, APST, host memory buffer, timestamp, KATO, HCTM, non-operational power state config, read recovery level, PLM config/window, LBA status interval, host behavior, sanitize, endurance event config, IOCS profile, software progress, host ID extended/non-extended, reservation notification mask, reservation persistence, namespace write protect, and live migration controller data queue.

## Behavior
Each case asserts exact command shape: opcode, NSID, FID, save/select bits, CDW packing, data buffer direction/length, timeout where applicable, result propagation, and returned data copies. Shared tail-call paths are tested for both NVMe status-code errors and negative kernel errors.

## Relevance
Protects the correctness of high-level feature helper APIs that build low-level NVMe admin passthrough commands.
