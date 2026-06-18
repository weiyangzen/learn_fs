# File Research: sources/virtualization/nvme-cli/plugins/inspur/inspur-utils.h

This header defines the packed Inspur vendor log payload consumed by `inspur-nvme.c`.

Constants:
- Byte-size helpers from 128 bytes through 64 KiB.
- `VENDOR_SMART_LOG_PAGE = 0xc0`.

Packed structures:
- `r1_cap_transtime_t`: two 16-bit capacitor transition time fields inside a 32-bit word.
- `vendor_warning_str`: a 64-bit-style warning bit layout represented as bitfields across rebuild, self-test, internal, capacitance, I/O, firmware, spare, lifetime, temperature, and MCU-disable indicators.
- `r1_vendor_log_nandctl_count_t`: NAND controller read/program/erase counters, rebuild/retry counters, and bad-block counters.
- `r1_wearlvl_vendor_log_count_t`: wear-leveling and GC counters.
- `vendor_media_err_t`: ten LBA error entries.
- `r1_vendor_log_io_err_t`: protection, DMA, read/write fail, and LBA error counters.
- `r1_cli_vendor_log_t`: the full packed vendor-log payload, combining power/temperature/capacitor status, warning unions, PCIe counters, NAND/wear-leveling sections, E2E counters, and media-error arrays.

Role:
- This file is the binary ABI definition for Inspur log page `0xc0`. It is tightly coupled to fixed device firmware layout and is not independently executable.
