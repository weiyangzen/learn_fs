# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/usb/usba/usba_devdb.h

## Role

Defines the public USBA device database record used to map USB device identity/preferences to configuration and driver choices.

## Key Interfaces

- `usba_configrec_t` stores selection string, vendor ID, product ID, configuration index, serial number, pathname, and preferred driver.
- Declares `usba_devdb_get_user_preferences()` to look up a matching user preference record.
- Declares `usba_devdb_refresh()` to reload or refresh the database.

## Risk Notes

This database can influence driver binding/configuration. Matching fields such as serial number and pathname must be interpreted consistently with parser and enumeration code.
