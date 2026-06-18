# File Research: sources/virtualization/nvme-cli/libnvme/src/nvme/nvme-cmds-fabrics.h

## Role

Inline helpers for NVMe over Fabrics specific commands and fabrics-related log pages.

## Helpers

- `nvme_init_get_log_discovery()`: initializes Get Log Page for the discovery log with LPO.
- `nvme_init_get_log_host_discovery()`: initializes host discovery log retrieval and encodes `allhoste` in LSP.
- `nvme_init_get_log_ave_discovery()`: initializes AVE discovery log retrieval.
- `nvme_init_get_log_pull_model_ddc_req()`: initializes pull model DDC request log retrieval.
- `nvme_init_set_property()`: initializes Fabrics Set Property using `nvme_admin_fabrics`, fabrics property-set type in `nsid`, register width in `cdw10`, offset in `cdw11`, and value split into `cdw12/cdw13`.
- `nvme_init_get_property()`: initializes Fabrics Get Property using fabrics property-get type and property offset.

## Dependencies

Includes `nvme/ioctl.h`, `nvme/nvme-cmds-base.h`, and `nvme/nvme-types-fabrics.h`.

## Notes

The property helpers rely on `nvme_is_64bit_reg(offset)` to encode register width. Like other command headers, this file only prepares passthrough structures and does not execute them.
