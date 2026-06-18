# File Research: sources/virtualization/nvme-cli/plugins/ocp/ocp-fw-activation-history.h

## Role

Defines the packed OCP firmware activation history log structures and declares the retrieval command handler.

## Structures

`struct fw_activation_history_entry` contains:

- version number
- entry length
- activation count
- NVMe timestamp
- power cycle count
- previous firmware revision
- new firmware revision
- slot number
- commit action
- result
- reserved fields

`struct fw_activation_history` contains:

- log ID
- valid entry count
- 20 activation history entries
- reserved padding
- log page version
- 16-byte GUID represented as two `__le64` values

Both structures are packed to match on-device log layout.

## Public Declaration

- `ocp_fw_activation_history_log()`

## Dependencies

Includes:

- `libnvme.h`
- `common.h`

Forward declares `struct command` and `struct plugin`.

## Notes

This header is consumed by retrieval code and OCP print implementations. It is part of the binary contract for parsing OCP firmware activation history data.
