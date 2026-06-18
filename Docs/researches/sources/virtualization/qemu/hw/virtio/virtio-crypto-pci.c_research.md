# File Research: sources/virtualization/qemu/hw/virtio/virtio-crypto-pci.c

## Purpose
Implements the PCI transport wrapper for virtio-crypto.

## Key Elements
- Defines `VirtIOCryptoPCI`, embedding `VirtIOPCIProxy` and `VirtIOCrypto`.
- Exposes default-on `ioeventfd` and `vectors=2`.
- `virtio_crypto_pci_realize()` requires a valid `cryptodev` link before realizing the child device and forces virtio 1.0.
- Class init sets device category `MISC`, PCI class `PCI_CLASS_OTHERS`, and the realize callback.
- Registers `virtio-crypto-pci` through virtio-pci type registration.

## Dependencies
Uses virtio-pci, `virtio-crypto.h`, qdev properties, QOM, and QAPI errors.

## Behavior/Risks
Virtio-crypto is modern-only here through `virtio_pci_force_virtio_1()`. Missing `cryptodev` is a realization error.
