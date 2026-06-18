# File Research: sources/virtualization/nvme-cli/util/types.c

## Role

`types.c` implements conversion helpers for NVMe-specific integer widths, 128-bit values, UUID/firmware display strings, timestamps, and a terminal progress spinner.

## Integer Conversion

- `le128_to_cpu()` copies 16 bytes into `nvme_uint128_t`, converts each 32-bit word from little endian, and reorders words so word zero is most significant.
- `int128_to_double()` converts a 16-byte little-endian integer buffer into a `long double` by accumulating from most significant byte to least significant byte.
- `int_to_long()` is a private helper that converts arbitrary bit widths up to 64 bits from little-endian byte data into `uint64_t`.
- `int48_to_long()` and `int56_to_long()` call `int_to_long()` with 48 and 56 bits.
- `uint128_t_to_double()` converts `nvme_uint128_t` word-by-word to `long double`, treating each word as base 2^32.

## 128-bit String Formatting

`__uint128_t_to_string()` converts `nvme_uint128_t` to decimal text without native `__uint128_t`, repeatedly dividing the four 32-bit words by 10 and prepending digits into a static 60-byte buffer.

The public wrappers are:

- `uint128_t_to_string()` for plain decimal;
- `uint128_t_to_l10n_string()` for locale thousands separators;
- `uint128_t_to_si_string()` for byte-scaled SI output, multiplying by `bytes_per_unit`, using `suffix_si_get_ld()`, and formatting as `"%.2Lf %sB"` in a static 40-byte buffer.

## Other Display Helpers

- `util_uuid_to_string()` calls `libnvme_uuid_to_string()` into a static UUID string buffer.
- `util_fw_to_string()` converts an 8-byte firmware field to printable ASCII, replacing non-printable bytes with `.`.
- `convert_ts()` treats the input `time_t` as milliseconds since epoch, formats UTC with `gmtime_r()` and `strftime("%Y-%m-%dD|%H:%M:%S")`, then appends millisecond digits.
- `util_spinner()` prints a carriage-return progress bar with a rotating character and clamps percent to `[0, 1]`.

## Dependencies

Uses `<ccan/endian/endian.h>` for endian helpers, libnvme for UUID constants/conversion, `types.h`, and `util/suffix.h`.

## Notable Edge Cases

- Several functions return pointers to static buffers, so results are overwritten by later calls and are not thread-safe.
- `uint128_t_to_l10n_string()` assumes `localeconv()->thousands_sep` is non-NULL before `strlen()`.
- The localized decimal conversion uses static storage and inserts separators while building digits backward.
- `convert_ts()` output format contains `D|` between date and time, matching the code but differing from common ISO 8601 `T`.
- `util_spinner()` uses static progress/spinner state and writes directly to stdout.

## Research Notes

This file avoids compiler-native 128-bit integer dependencies by representing NVMe 128-bit counters as four 32-bit words. That portability choice shapes both decimal conversion and JSON support elsewhere in this group.
