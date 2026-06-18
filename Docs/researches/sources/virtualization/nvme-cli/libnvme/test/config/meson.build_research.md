# File Research: sources/virtualization/nvme-cli/libnvme/test/config/meson.build

## Purpose
Meson test definitions for libnvme config fixtures.

## Behavior
Requires `diff`, builds `test-config-dump`, `test-hostnqn-order`, and `test-psk-json`, then registers tests through `config-diff.sh`. It wires sysfs tarballs and JSON fixtures for PCIe/config merge tests, host identity order tests, and TLS key JSON tests.

## Relevance
Connects deterministic config fixtures into the libnvme test suite.
