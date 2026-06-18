# File Research: sources/virtualization/nvme-cli/plugins/ymtc/ymtc-nvme.c

Implements the YMTC vendor plugin command `smart-log-add`.

Key elements:
- Registers through `ymtc-nvme.h` using `CREATE_CMD`.
- Fetches a vendor-specific SMART log page with log ID `0xca` via `nvme_get_nsid_log`.
- Supports `--namespace-id` and `--raw-binary`.
- In formatted mode, identifies the controller to obtain firmware revision and prints selected normalized/raw vendor SMART attributes.
- Converts several 48-bit raw fields with `int48_to_long`.
- Handles allocation failures for temporary normalized/raw buffers and reports NVMe positive status codes.

Dependencies:
- Uses `ymtc-utils.h` for log item layout and attribute indexes.
- Uses nvme-cli parsing/opening helpers, raw dump helper `d_raw`, and libnvme transport handles.

Notes:
- Raw fields are accessed through casts like `*(uint16_t *)raw`; this assumes acceptable alignment and host endianness for this plugin’s target behavior.
