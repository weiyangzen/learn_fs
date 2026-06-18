# File Research: sources/virtualization/nvme-cli/unit/test-uint128-si.c

C unit test for converting 128-bit NVMe counters to SI strings.

Key elements:
- Defines `U128` helper from four 32-bit words.
- Tests zero, small values, a mixed large value, max 128-bit value, and several sector-count-style values with `bytes_per_unit = 1000 * 512`.
- Expected units include B, TB, RB, and QB.

Role:
- Verifies `uint128_t_to_si_string` formatting and scaling.
