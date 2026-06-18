# File Research: sources/virtualization/nvme-cli/plugins/inspur/inspur-nvme.c

This file implements the single Inspur plugin command `nvme-vendor-log`.

Main behavior:
- `nvme_get_vendor_log()` opens the target device, allocates a 4 KiB stack buffer, retrieves vendor log page `VENDOR_SMART_LOG_PAGE` (`0xc0`) with `nvme_get_log_simple()`, and prints parsed output.
- `show_r1_vendor_log()` formats a packed `r1_cli_vendor_log_t` structure from `inspur-utils.h`. It prints:
  - Device health state.
  - Commit ID and MCU telemetry.
  - Power, voltage, current, temperature, capacitor transition timing, capacitor health.
  - Warning/current and warning-history bitfields with named bit output.
  - NAND bytes written per partition.
  - Per-partition I/O/protection/DMA/LBA error counters.
  - PCIe reset/link/error counters.
  - NAND controller counters for read/program/erase, rebuild, retry, and bad-block categories.
  - Temperature throttling counters.
  - Wear-leveling counters.
  - End-to-end check counters.
- `show_r1_media_err_log()` prints up to 10 read-error LBAs for each of four media groups.

Data handling:
- Uses explicit little-endian conversion through `le32_to_cpu()` and `le64_to_cpu()` for most numeric fields.
- Interprets temperature-like fields as Kelvin and prints Celsius by subtracting 273.
- Uses `PRIu64` for 64-bit counters.

Notable quirks:
- `show_r1_vendor_log()` prints some final counters with index `i` after loops, leaving `i == 4`; the prefix is cosmetic but misleading.
- The command always fetches `sizeof(r1_cli_vendor_log_t)` into a 4 KiB local buffer; this assumes the packed layout remains within 4 KiB.
