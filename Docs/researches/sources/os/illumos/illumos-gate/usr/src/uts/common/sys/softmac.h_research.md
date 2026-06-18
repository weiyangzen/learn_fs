# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/softmac.h

## Role

Public softmac interface header for creating, destroying, holding, releasing, and recreating softmac devices.

## Interfaces

Declares `softmac_create`, `softmac_destroy`, `softmac_hold_device`, `softmac_rele_device`, and `softmac_recreate`.

## Dependencies

Pulls in DDI, MAC, and DLS types. The hold/release API exposes `dls_dev_handle_t`, indicating this header bridges softmac lifecycle with the data-link services device layer.
