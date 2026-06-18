# File Research: sources/virtualization/nvme-cli/util/types.h

## Role

`types.h` declares NVMe type conversion helpers and small display utilities used across nvme-cli.

## Constants And Inline Helpers

- `ABSOLUTE_ZERO_CELSIUS` is `-273`.
- `STR_LEN` is `100`, used by JSON formatting helpers.
- `kelvin_to_celsius()` adds absolute zero offset.
- `celsius_to_fahrenheit()` converts integer Celsius to Fahrenheit.
- `kelvin_to_fahrenheit()` combines the previous two conversions.

## 128-bit Type

`union nvme_uint128` stores a 128-bit value as either:

- `__u8 bytes[16]`; or
- `__u32 words[4]`, with `[0]` documented as the most significant word.

`typedef union nvme_uint128 nvme_uint128_t;`

## Declared Functions

- endian/width conversion: `le128_to_cpu()`, `int128_to_double()`, `int48_to_long()`, `int56_to_long()`;
- 128-bit formatting/conversion: `uint128_t_to_string()`, `uint128_t_to_l10n_string()`, `uint128_t_to_si_string()`, `uint128_t_to_double()`;
- display helpers: `util_uuid_to_string()`, `util_fw_to_string()`;
- timestamp conversion: `convert_ts()`;
- progress display: `util_spinner()`.

## Dependencies

Includes `<stdint.h>`, `<time.h>`, and `<libnvme.h>` for fixed-width and NVMe-specific types/constants.

## Research Notes

The conversion helpers operate on NVMe wire-format byte arrays and project-defined 128-bit values. Several returned strings come from static storage in `types.c`; callers should copy them if they need stable values across subsequent calls.
