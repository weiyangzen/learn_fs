# File Research: sources/virtualization/nvme-cli/plugins/solidigm/solidigm-get-drive-info.c

Solidigm drive hardware information command implementation.

Main command:
- `sldgm_get_drive_info`: prints FTL unit size in normal or JSON format.

Flow:
- Opens the target with nvme-cli helpers.
- Accepts only normal or JSON output.
- Scans libnvme topology.
- Resolves either a controller’s first namespace or a namespace handle.
- Identifies namespace with `libnvme_ns_identify`.
- Requires `ns.nsfeat & 0x10`, described as performance options availability.
- Finds current LBA format, computes LBA size as `1 << ds`, and computes `FTL_unit_size = (npwg + 1) * lba_size / 1024`.

Output:
- Normal: `FTL_unit_size: <value>`
- JSON: object with `FTL_unit_size`.

Relevance:
- Reports write granularity-like information derived from namespace preferred write granularity and LBA size, useful for alignment/performance decisions above the block layer.
