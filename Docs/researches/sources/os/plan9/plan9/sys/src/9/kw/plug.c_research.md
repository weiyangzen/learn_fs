# File Research: sources/os/plan9/plan9/sys/src/9/kw/plug.c

## Role

Static kernel configuration for the Kirkwood Plan 9 build. It declares compiled-in device tables, link functions, SD interfaces, UART implementations, IP protocol initializers, boot settings, and the embedded textual config file.

This is configuration glue. It includes storage-relevant device selection through flash, SD, AoE, USB, and filesystem devices.

## Main Interfaces

- `devtab[]`: root/cons/env/pipe/proc/mnt/srv/rtc/arch/aoe/sd/fs/flash/twsi/ether/ip/uart/usb and other devices.
- `links()`: invokes compiled-in linker registration functions.
- `sdifc[]`: includes `sdaoeifc`.
- `physuart[]`: includes `kwphysuart`.
- `ipprotoinit[]`: TCP, UDP, IP interface, ICMP, ICMPv6, IP mux.
- Global config:
  - `cpuserver = 1`
  - `i8250freq = 3686000`
  - `conffile`
  - `kerndate`
  - `configfile[]`

## Important Behavior

- Registers Kirkwood Ethernet, architecture, flash, network medium, loopback, and EHCI USB support.
- Embeds the kernel configuration as a byte array terminated by zero.
- The embedded config comments identify target boards such as SheevaPlug, OpenRD client, GuruPlug, and DreamPlug.

## Dependencies And Assumptions

- Depends on each referenced `Dev`, link function, SD interface, UART, and IP initializer being linked.
- The byte-array config must match build-time expectations.

## Notable Risks

- Stale static device tables can include dead or missing devices.
- The embedded config is not human-editable in this generated C form.
