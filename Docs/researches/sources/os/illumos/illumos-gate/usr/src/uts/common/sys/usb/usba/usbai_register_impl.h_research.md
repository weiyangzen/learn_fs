# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/usb/usba/usbai_register_impl.h

## Role

Defines private state used while building a USB client descriptor tree during registration.

## Key Interfaces

- Defines binary descriptor dump formatting constants.
- Defines `USBA_ALL` sentinel for building all configurations/interfaces.
- `usba_reg_state_t` tracks current devinfo, current config/interface/alternate/endpoint nodes, last processed descriptor type, selected interface/configuration, total configuration length, current raw descriptor pointer/type/length, current config string, requested parse level, descriptor-tree root, and number of configurations.

## Design Notes

Warlock annotations mark descriptor tree and client registration fields as changed only at attach time.

## Risk Notes

Descriptor tree construction depends on correct state-machine placement of class/vendor-specific descriptors and correct parse-level filtering. Mistakes affect every client using `usb_get_dev_data()`.
