# File Research: sources/virtualization/nvme-cli/libnvme/test/ioctl/identify.c

## Purpose
Mock-ioctl test suite for NVMe Identify command initializer helpers.

## Test Coverage
Covers identify namespace/controller, active namespace list, namespace descriptors, NVM set list, CSI namespace/controller forms, ZNS identify namespace/controller, CSI active namespace list, independent namespace identify, allocated namespace/list, namespace controller list, controller list, primary/secondary controller structures, namespace granularity, UUID list, domain list, endurance group list, CSI allocated namespace list, command set structure, namespace user data format, and CSI namespace user data format.

## Behavior
Each test builds a mock admin identify command with expected CNS, NSID, CDW11/CDW14 fields and data length, executes passthrough, and compares copied output data. Error tests verify both NVMe status code and kernel errno propagation.

## Relevance
Validates the libnvme identify API layer, which is foundational for discovering NVMe controller, namespace, command-set, and endurance/domain capabilities.
