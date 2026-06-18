# File Research: sources/virtualization/libblockdev/src/plugins/nvdimm.h

## Role
Public header for the deprecated NVDIMM plugin.

## Public Model
- Defines `BDNVDIMMError` for tech unavailability, namespace failures, parse/no-exist conditions, and invalid namespace modes.
- Defines namespace mode enum values for raw, sector, memory, dax, fsdax, devdax, and unknown.
- Declares `BDNVDIMMNamespaceInfo`, holding namespace dev name, mode, size, UUID, sector size, associated block device, and enabled state.

## API Surface
Declares lifecycle, availability, mode string conversion, block-device-to-namespace lookup, namespace enable/disable, single namespace info, namespace listing, namespace reconfiguration, and supported sector-size lookup.
