# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/sata/adapters/ahci/ahciem.h

## Role

`ahciem.h` defines the private ioctl interface for AHCI enclosure-management LED services.

## Ioctls

The ioctl base is `AHCI_EM_IOC`, with:
- `AHCI_EM_IOC_GET`: read enclosure-management LED status.
- `AHCI_EM_IOC_SET`: modify LED state.

The interface supports up to 32 ports.

## Data Structures

`ahci_em_led_state_t` defines LED bits:
- identify enable.
- fault enable.
- activity disable.

`AHCI_EM_FLAG_CONTROL_ACTIVITY` marks activity LED control support.

`ahci_ioc_em_get_t` reports port count, flags, and per-port status array.

`ahci_ioc_em_set_t` carries target port, operation, LED bits, and padding. Set operations are add, remove, or replace.

## Research Notes

This is a small private AHCI management ABI. It maps user/admin LED intent onto AHCI enclosure-management state tracked in `ahcivar.h`.
