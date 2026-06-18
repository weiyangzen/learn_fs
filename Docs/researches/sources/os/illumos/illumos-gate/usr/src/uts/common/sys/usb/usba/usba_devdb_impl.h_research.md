# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/usb/usba/usba_devdb_impl.h

## Role

Provides private implementation definitions for parsing and storing the USBA USB device configuration map.

## Key Interfaces

- Defines `USBCONF_FILE` as `/etc/usb/config_map.conf` and a static `usbconf_file` variable.
- `usba_devdb_info_t` wraps a `usba_configrec_t` with an AVL tree link.
- `config_field_t` enumerates parser fields for selection, vendor, product, configuration index, serial number, pathname, driver, and none.
- `usba_cfg_varlist[]` maps textual config-file variable names to parser field identifiers.

## Design Notes

The header includes kernel object lexer/parser support and AVL support, indicating the config map is parsed in-kernel and stored for lookup.

## Risk Notes

Because this header defines static data, inclusion discipline matters. Field names must remain synchronized with `/etc/usb/config_map.conf` syntax and lookup code.
