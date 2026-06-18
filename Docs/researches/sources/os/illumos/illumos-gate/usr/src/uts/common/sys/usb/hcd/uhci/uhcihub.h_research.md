# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/usb/hcd/uhci/uhcihub.h

UHCI root-hub helper header. It declares root-hub initialization, control request handling, status-change callback, interrupt-pipe cleanup, and interrupt-pipe resource allocation.

It also defines small command constants for port enable/disable operations and port power enable/disable actions.

This file is intentionally narrow: it exposes just enough root-hub behavior for UHCI core and utility code without defining the full root-hub state, which lives in `uhcid.h`.
