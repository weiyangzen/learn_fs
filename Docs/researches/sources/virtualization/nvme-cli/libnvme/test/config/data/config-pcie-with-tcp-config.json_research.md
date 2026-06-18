# File Research: sources/virtualization/nvme-cli/libnvme/test/config/data/config-pcie-with-tcp-config.json

## Purpose
JSON config fixture with two hosts and TCP subsystem ports.

## Contents
Defines two host entries, each with host NQN/host ID and one subsystem `nqn.io-1`. Each subsystem has two TCP ports at `192.168.154.144` with services `4420` and `4421`, both using `dhchap_key:"none"`.

## Relevance
Exercises merging mocked PCIe/sysfs topology with explicit TCP fabrics configuration.
