# File Research: sources/os/bsd/freebsd-src/sbin/ipf/libipf/ionames.c

Static IPv4 option-name table for IPFilter rule parsing and printing.

Key behavior:
- Defines `ionames[]`, mapping option numeric values to bitmask bits, minimum lengths, and rule text names.
- Includes legacy/RFC options such as `rr`, `ts`, `lsrr`, `ssrr`, `sec`, `cipso`, `rtralrt`, and `ah`.
- Provides both `sec` and `sec-class` names for `IPOPT_SECURITY`.

Research notes:
- The duplicate security option entry is intentionally handled by printers that skip the second table row after printing normal security.
