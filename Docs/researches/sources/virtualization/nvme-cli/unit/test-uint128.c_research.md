# File Research: sources/virtualization/nvme-cli/unit/test-uint128.c

C unit test for 128-bit integer string formatting.

Key elements:
- Tests raw decimal conversion for zero, small values, a mixed large value, and max `uint128`.
- Tests localized formatting under `fr_FR.utf-8`, expecting a thousands separator for `1000`.
- Skips locale-specific assertion if the system locale or thousands separator is unavailable.

Role:
- Guards `uint128_t_to_string` and `uint128_t_to_l10n_string`.
