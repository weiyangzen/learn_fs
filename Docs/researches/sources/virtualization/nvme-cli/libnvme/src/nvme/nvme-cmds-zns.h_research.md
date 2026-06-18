# File Research: sources/virtualization/nvme-cli/libnvme/src/nvme/nvme-cmds-zns.h

## Role

Inline helper header for Zoned Namespace command set initialization.

## Helpers

- `nvme_init_get_log_zns_changed_zones()`: initializes Get Log Page for changed zones using CSI ZNS.
- `nvme_init_zns_identify_ns()`: initializes CSI namespace identify for ZNS namespace data.
- `nvme_init_zns_identify_ctrl()`: initializes CSI controller identify for ZNS controller data.
- `nvme_init_zns_mgmt_send()`: initializes Zone Management Send with SLBA, action, select-all, action-specific option, zone management field, and optional data.
- `nvme_init_zns_mgmt_recv()`: initializes Zone Management Receive with SLBA, receive action, action-specific fields, transfer length, and data buffer.
- `nvme_init_zns_report_zones()`: wraps management receive for normal or extended report zones, with partial-report control.
- `nvme_init_zns_append()`: initializes Zone Append with zone start LBA, NLB, control, command extension value, directive-specific field, data, and metadata.

## Dependencies

Includes `nvme/ioctl.h`, `nvme/nvme-cmds-base.h`, and `nvme/nvme-types-zns.h`.

## Notes

`nvme_init_zns_append()` only encodes CEV when the command control field indicates a non-zero command extension type.
