# File Research: sources/os/plan9/9front/sys/src/cmd/nusb/lib/parse.c

This file parses standard USB device and configuration descriptors into the in-memory structures from `usb.h`. `parsedev()` validates the device descriptor, records USB version, CSP, USB3 endpoint-zero max packet interpretation, class, configuration count, vendor/product/device ids, string descriptor ids, and endpoint zero defaults.

`parseiface()` validates interface descriptors, derives CSP from interface or device class, creates/looks up `Iface` entries by interface number, alternate setting, and CSP, links them into the configuration, and associates endpoint zero with the first interface of configuration zero.

`parseendpt()` validates endpoint descriptors, derives direction/type/address, creates endpoint ids that remain unique across type/direction/interface/alternate settings, merges same-interface IN/OUT endpoints into `Eboth` when possible, stores max packet size, high-bandwidth transaction count, attributes, polling interval, and attaches endpoints to both the device endpoint chain and the interface endpoint array.

`parsedesc()` walks the variable descriptor stream following a configuration descriptor. It dispatches standard interface and endpoint descriptors to the parsers and stores all other device-specific descriptors as raw `Desc` records tagged with the current configuration, most recent interface, and most recent endpoint. `parseconf()` validates the configuration header, records configuration value/attributes/power, checks total length, and parses the remaining descriptor stream.
