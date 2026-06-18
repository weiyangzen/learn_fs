# File Research: sources/virtualization/nvme-cli/ccan/ccan/minmax/minmax.h

- Purpose: type-checked min/max/clamp macros.
- Key APIs: `min`, `max`, `clamp`, `min_t`, `max_t`, and `clamp_t`.
- Requirements: hard errors unless statement expressions and `typeof` are available.
- Safety: stores arguments in temporaries to avoid double evaluation and checks type compatibility when supported.
