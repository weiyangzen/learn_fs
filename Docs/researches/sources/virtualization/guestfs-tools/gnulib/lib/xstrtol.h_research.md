# File Research: sources/virtualization/guestfs-tools/gnulib/lib/xstrtol.h

Header for robust string-to-integer parsers.

Defines:
- `enum strtol_error` values:
  - `LONGINT_OK`
  - `LONGINT_OVERFLOW`
  - `LONGINT_INVALID_SUFFIX_CHAR`
  - combined overflow/suffix error
  - `LONGINT_INVALID`

Declares:
- `xstrtol`
- `xstrtoul`
- `xstrtoll`
- `xstrtoull`
- `xstrtoimax`
- `xstrtoumax`

Research relevance: parse-status contract for gnulib numeric conversion helpers.
