# File Research: sources/os/bsd/freebsd-src/sbin/devd/syscons.conf

## Purpose
Switches syscons keyboard device when USB keyboard `ukbd0` appears or disappears.

## Main Elements
- Attach `ukbd0`: `service syscons setkeyboard /dev/ukbd0`.
- Detach `ukbd0`: `service syscons setkeyboard /dev/kbd0`.

## Dependencies And Integration
Installed in the console-tools group.
