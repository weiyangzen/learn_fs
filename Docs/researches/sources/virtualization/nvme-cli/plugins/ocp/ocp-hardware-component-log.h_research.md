# File Research: sources/virtualization/nvme-cli/plugins/ocp/ocp-hardware-component-log.h

## Role

Defines the OCP Hardware Component Log data structures, component ID enum, and public functions.

## Constants

- `HWCOMP_RSVD2_LEN`: 14
- `HWCOMP_SIZE_LEN`: 16
- `HWCOMP_RSVD48_LEN`: 16

## Structures

`struct hwcomp_desc` is packed and represents a hardware component descriptor prefix:

- `date_lot_size`
- `add_info_size`
- `id`
- `mfg`
- `rev`
- `mfg_code`

`struct hwcomp_log` is packed and represents the fetched log header plus descriptor pointer:

- version
- reserved bytes
- GUID
- 16-byte size field
- reserved bytes
- `struct hwcomp_desc *desc`

`struct hwcomp_desc_entry` is an unpacked parsed descriptor view:

- pointer to descriptor
- decoded date/lot size and pointer
- decoded additional-info size and pointer
- total descriptor size

## Component Enum

`enum hwcomp_id` defines standard and vendor component identifiers:

- Reserved: `0`
- ASIC through born-on date: `1` through `12`
- Vendor range start: `0x8000`
- Max: `0xffff`

## Public Declarations

- `ocp_hwcomp_log()`
- `hwcomp_id_to_string()`

## Dependencies

Includes:

- `cmd.h`
- `common.h`
- `ocp-nvme.h`

## Notes

The structures describe on-device binary layout and are consumed by both retrieval and print modules. The `desc` pointer in `struct hwcomp_log` is not an on-wire field; retrieval code deliberately fetches only up to its offset for the header.
