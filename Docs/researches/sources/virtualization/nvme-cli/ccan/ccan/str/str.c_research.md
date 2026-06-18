# File Research: sources/virtualization/nvme-cli/ccan/ccan/str/str.c

- Purpose: implementation file for CCAN string helpers.
- Key API: `strcount`.
- Behavior: counts non-overlapping occurrences of `needle` in `haystack` using `strstr` and advances by needle length.
