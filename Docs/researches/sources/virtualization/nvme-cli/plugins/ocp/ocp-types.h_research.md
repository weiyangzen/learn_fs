# File Research: sources/virtualization/nvme-cli/plugins/ocp/ocp-types.h

## Role

`ocp-types.h` is a tiny helper header for OCP-specific bitfield access. It wraps the nvme-cli `NVME_GET` and `NVME_SET` macros with OCP-prefixed field names:

- `OCP_GET(value, name)` expands to `NVME_GET(value, OCP_##name)`.
- `OCP_SET(value, name)` expands to `NVME_SET(value, OCP_##name)`.

## Defined Field

The file defines `enum nvme_ocp_enable_ieee1667_silo` with:

- `NVME_OCP_ENABLE_IEEE1667_SILO_SHIFT = 31`
- `NVME_OCP_ENABLE_IEEE1667_SILO_MASK = 1`

This describes a one-bit OCP IEEE1667 silo enable flag at bit 31.

## Dependencies and Integration

The file does not include other headers directly. It assumes callers include the nvme-cli headers that define `NVME_GET` and `NVME_SET` before using these macros. It is likely included by OCP command code that wants compact feature-field accessors.

## Notable Risks

There is no include dependency enforcement in this header. If included before the base NVMe bitfield macros are available, compilation will fail at macro use sites rather than at include time.
