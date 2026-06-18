# File Research: sources/os/bsd/freebsd-src/sbin/devd/moused.conf

## Purpose
Starts or stops `moused` for mouse-like device nodes.

## Main Elements
- Starts `moused` for `atp`, `ums`, `wsp`, and `input/event` device creation.
- Stops `moused` for `ums` destroy events.

## Dependencies And Integration
Matches DEVFS CDEV create/destroy notifications and calls `service moused`.
