# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/usb/hcd/openhci/ohci_polled.h

OHCI polled-mode support header for console input/output during firmware/debugger contexts. It defines raw keyboard buffer sizing, input/output mode flags, in-use flags, and `ohci_polled_t`.

`ohci_polled_t` stores the owning controller, input pipe, dummy and interrupt EDs, scan-code buffer, saved done-head fragments, nested polled-entry count, USB device/endpoint identity, and a no-sync workaround flag.

The design explicitly supports nested entry/exit paths such as kmdb to firmware prompt and back. Warlock annotations mark fields protected by polled-mode execution rather than normal mutexes.

This file is critical for keeping OS-mode interrupt processing and polled-mode keyboard access from corrupting each other.
