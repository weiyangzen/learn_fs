# File Research: sources/virtualization/nvme-cli/plugins/netapp/netapp-nvme.h

## Role

Command registration header for the NetApp nvme-cli plugin.

## Registered Plugin

Plugin name: `netapp`.

Description: `NetApp vendor specific extensions`.

Version source: `NVME_VERSION`.

## Registered Commands

- `smdevices`: mapped to `netapp_smdevices`, displays NetApp E-Series volume information.
- `ontapdevices`: mapped to `netapp_ontapdevices`, displays NetApp ONTAP namespace/device information.

## Dependency Relationship

Included by `netapp-nvme.c` with `CREATE_CMD` defined. Uses `cmd.h` and `define_cmd.h` for nvme-cli macro expansion.

## Notes

The file is declarative and contains no runtime logic.
