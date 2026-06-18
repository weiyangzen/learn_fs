# File Research: sources/os/bsd/freebsd-src/sbin/devd/bluetooth.conf

## Purpose
Starts and stops Bluetooth service for USB Bluetooth device attach/detach events.

## Main Elements
- `attach 100` for `ubt[0-9]+` runs `service bluetooth quietstart`.
- `detach 100` for `ubt[0-9]+` runs `service bluetooth quietstop`.

## Dependencies And Integration
Installed when Bluetooth support is enabled. Uses attach/detach device-name matching.
