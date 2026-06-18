# File Research: sources/os/plan9/9front/sys/src/cmd/nusb/serial/acm.c

This file implements CDC ACM serial-device support for the shared nusb serial framework. It probes functional descriptors for call-management and abstract-control-management records, records the data-interface id from the call-management descriptor, and installs ACM serial operations when both required descriptors are present.

`acmsetparam()` sends a CDC `SET_LINE_CODING` class/interface request containing baud rate, stop bits, parity, and data bits. `acminit()` initializes defaults to 9600 baud, one stop bit, eight data bits, and applies them. `acmwait4data()` releases the serial lock while blocking on reads from the IN endpoint, then reacquires it.

`acmfindeps()` locates the data interface recorded during probe, finds bulk IN and OUT endpoints, optionally notes an interrupt endpoint if the serial framework expects one, and opens the data endpoints via `openeps()`. The installed `Serialops` supplies init, set-parameter, wait-for-data, and endpoint-finding behavior.
