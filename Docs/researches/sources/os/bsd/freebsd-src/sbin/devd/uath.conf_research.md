# File Research: sources/os/bsd/freebsd-src/sbin/devd/uath.conf

## Purpose
Loads firmware for supported Atheros USB wireless devices.

## Main Elements
- Multiple `notify 100` rules match USB DEVICE ATTACH events.
- Rules match vendor/product combinations for Accton, Atheros, Conceptronic, D-Link, Gigaset, Global Sun, Netgear, U-MEDIA, Wistron, Z-Com, and related AR5523 devices.
- Action runs `/usr/sbin/uathload -d /dev/$cdev`.

## Dependencies And Integration
Installed when USB support is enabled. Matches USB event variables emitted by the kernel/devctl path.
