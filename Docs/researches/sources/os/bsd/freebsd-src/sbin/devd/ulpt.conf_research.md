# File Research: sources/os/bsd/freebsd-src/sbin/devd/ulpt.conf

## Purpose
Provides an example USB printer rule.

## Main Elements
- Entire notify rule is commented out.
- Example matches USB INTERFACE ATTACH for printer class/subclass/protocol.
- Example action changes ownership of `/dev/$cdev`.

## Dependencies And Integration
Installed when USB support is enabled, but inert by default.
