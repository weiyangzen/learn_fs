# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/usb/clients/usbecm/usbecm.h

Internal USB CDC ECM Ethernet driver state header. It defines PM state, MAC statistics, device-specific operation callbacks, and the main `usbecm_state` structure.

`usbecm_state` owns USBA handles, MAC handle, serialization object, control/data interface numbers, endpoint data, ECM descriptor compatibility data, MAC address and packet filter state, pipe handles/states, receive queue, TX count, statistics, initialization flags, MAC state, private device data, and device-specific ops.

Constants cover pipe states, MAC states, bulk timeouts, class request type composition, init flags, ECM statistics selectors/capability bits, ECM class-specific request codes, packet filter bits, debug masks, and byte-order helpers.

The file redefines simple `isdigit` and `toupper` macros locally, so consumers must be aware of macro namespace effects.
