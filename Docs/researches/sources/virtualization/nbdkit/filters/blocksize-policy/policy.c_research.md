# File Research: sources/virtualization/nbdkit/filters/blocksize-policy/policy.c

Purpose: filter that advertises and enforces NBD block-size policy, optionally rejecting requests that violate minimum/maximum/alignment constraints.

Key details:
- Configures `blocksize-error-policy`, `blocksize-minimum`, `blocksize-preferred`, `blocksize-maximum`, and `blocksize-write-disconnect`.
- Error policy modes are `allow`, `error`, and `strict-error`; `error` permits unaligned final tails by rounding the checked count up at EOF.
- `policy_block_size` merges user-configured constraints with backend-advertised constraints, synthesizing defaults when needed.
- `check_policy` rejects misaligned offsets, undersized counts, oversized data requests, and counts not divisible by minimum block size with `EINVAL`.
- `policy_pwrite` can force client disconnect on writes larger than `blocksize-write-disconnect`.
- `policy_can_extents` forces extents support so `.extents` can align backend results even when the plugin lacks native extents.
- Registered callbacks include `.block_size`, `.pread`, `.pwrite`, `.zero`, `.trim`, `.cache`, and `.extents`.

Risk notes:
- In `policy_config_complete`, the maximum multiple check uses `config_maximum % config_maximum`, which is always zero for nonzero values; it likely intended `config_maximum % config_minimum`. This weakens validation.
