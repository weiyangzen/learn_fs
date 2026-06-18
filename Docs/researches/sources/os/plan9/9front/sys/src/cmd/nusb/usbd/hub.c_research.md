# File Research: sources/os/plan9/9front/sys/src/cmd/nusb/usbd/hub.c

## Role

Implements USB hub configuration, polling, port state tracking, device enumeration, detach handling, and child hub management for `nusb/usbd`.

## Hub Setup

`newhub` creates either a root hub from `/dev/usb/...` controller state or a normal hub from USB hub descriptors. USB2 setup parses `DHub`, port power/removable maps, TT fields, and optionally enables multi-TT mode. USB3 setup parses `DSSHub` and sets hub depth.

After setup, each port is powered, optional indicators are enabled, the hub is added to the global hub list, and data I/O is opened.

## Enumeration

`work` loops forever, holding `hublock`, polling every hub and port in list order. Enumeration is intentionally serialized so default-address USB enumeration cannot race.

`enumhub` compares current and prior port status, handles suspend resume, detects attach, detach, lost-enable reconnects, and user-requested resets, then calls `portattach`, `portdetach`, or `portfail`.

`portattach` throttles repeated attach loops, resets non-USB3 ports, creates the kernel device with `newdev`, opens endpoint zero, assigns address, reads max packet size, configures descriptors, assigns stable hardware name, sets configuration 1, recursively handles hubs, and posts non-hub devices through `attachdev`.

## Failure Handling

`hubfail` detaches all ports and marks a hub failed. `closehub` removes a hub from the global list, detaches children, closes the device, and frees state. `portfail` detaches and disables or warm-resets the port depending on USB generation.

## Notable Details

The code does not use hub interrupt endpoints; it polls because root hubs must be polled anyway. Attach-loop throttling prevents unstable devices from repeatedly consuming enumeration.
