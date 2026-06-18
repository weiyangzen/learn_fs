# File Research: sources/virtualization/nvme-cli/util/suffix.h

## Role

`suffix.h` declares the human-readable suffix conversion API implemented by `suffix.c`.

## API

- `suffix_si_get(double *value)`: convert a double in place to the largest matching decimal SI unit and return suffix text.
- `suffix_si_parse(const char *str, char **endptr, uint64_t *val)`: parse decimal/SI-suffixed text into a `uint64_t`.
- `suffix_si_get_ld(long double *value)`: long-double SI formatter.
- `suffix_binary_get(long long *value)`: integer binary formatter with rounding.
- `suffix_dbinary_get(double *value)`: floating binary formatter.
- `suffix_binary_parse(const char *str, char **endptr, uint64_t *val)`: parse binary-suffixed text into a `uint64_t`.

## Dependencies

Includes `<inttypes.h>` and `<stdbool.h>`. The use of `uint64_t` comes through the integer type headers.

## Research Notes

The API mutates input numeric values during formatting. Callers must pass mutable storage and should preserve original values separately if needed.
