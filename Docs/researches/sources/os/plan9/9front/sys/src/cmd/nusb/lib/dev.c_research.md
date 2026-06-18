# File Research: sources/os/plan9/9front/sys/src/cmd/nusb/lib/dev.c

This file implements core USB device/endpoint lifecycle and control-transfer helpers for nusb drivers. It opens `/dev/usb/epN.M` control/data files, configures devices by reading descriptors, creates endpoint files through endpoint control messages, loads string descriptors, manages reference-counted `Dev` cleanup, and provides retrying USB control requests.

`openep()` creates or opens a kernel USB endpoint file for a parsed `Ep`, sets max packet size, transaction count, and polling interval, and returns a `Dev` for endpoint I/O. `opendev()` opens a control endpoint directory, stores path/id metadata, initializes fds, and sets a reference. `opendevdata()` opens the `data` file for an endpoint. `getdev()` accepts either a path or numeric device id, opens/configures endpoint zero, and stores the hash name used by served device names.

Descriptor loading uses `loaddevdesc()` for the device descriptor and string ids, and `loaddevconf()` for configurations. `configdev()` opens data if needed, loads the device descriptor, and loads all configurations. `closedev()` decrements references and frees endpoint/configuration/interface/descriptor trees, strings, paths, and fds.

`usbcmd()` constructs standard USB control request packets, writes them to the endpoint data file, optionally reads the reply, retries transient failures up to `Uctries`, and logs requests/replies when `usbdebug` is high. `unstall()`, `setconf()`, `setalt()`, and `devctl()` provide common endpoint recovery and configuration helpers.
