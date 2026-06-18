# File Research: sources/virtualization/nvme-cli/ccan/ccan/container_of/container_of.h

- Purpose: Linux-style enclosing-structure helpers.
- Key APIs: `container_of`, `container_of_or_null`, `container_off`, `container_of_var`, and `container_off_var`.
- Type safety: uses `check_types_match` when possible.
- Use: supports intrusive data structures such as CCAN list wrappers.
