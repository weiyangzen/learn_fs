# File Research: sources/virtualization/nvme-cli/plugins/mangoboost/mangoboost-nvme.h

This header registers the MangoBoost nvme-cli plugin.

Registered plugin:
- Name: `mangoboost`
- Description: `MangoBoost vendor specific extensions`
- Version: `NVME_VERSION`

Registered command:
- `id-ctrl`: calls the MangoBoost identify-controller wrapper in `mangoboost-nvme.c`.

The file uses the standard nvme-cli command generation macros and include pattern.
