# File Research: sources/os/plan9/9front/sys/src/9/xen/xen-public/io/xenbus.h

Imported Xen public XenBus state definitions.

Purpose:
- Defines the XenBus frontend/backend state machine enumeration.

Key content:
- Defines `enum xenbus_state`: unknown, initialising, init-wait, initialised, connected, closing, closed, reconfiguring, and reconfigured.
- Typedefs `XenbusState`.

Integration:
- Directly used by 9front’s xenstore/xenbus and virtual device setup paths.
- `sdxen.c` writes and waits on XenBus states while attaching virtual block devices.
- `blkif.h` documents the detailed block-device startup transitions using these states.

Risks/notes:
- State transition tolerance matters because peers may skip optional negotiation states.
