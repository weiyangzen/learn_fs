# sources/test-tools/fio/optgroup.c

Purpose: maps fio option category and category-group bitmasks to user-facing group names.

Important APIs/functions: `opt_group_from_mask` and `opt_group_cat_from_mask`, both backed by static `fio_opt_groups`, `fio_opt_cat_groups`, and `group_from_mask`.

Control flow: callers pass a mutable mask. `group_from_mask` returns null for invalid/all/zero masks, scans the configured table for the first matching bit, clears that bit from the caller mask, and returns the matching descriptor. Repeated calls enumerate all set groups.

State/persistence: static read-only group tables; caller-owned mask is mutated to track enumeration progress.

Dependencies/integration: includes `optgroup.h` and compiler compile-time assertions. Used by option help/output formatting to organize options.

Risks/test signals: table coverage must stay in sync with enum bits; new enum values without table entries will be silently skipped until the mask is exhausted. Tests should iterate every category/group bit and verify expected display names or intentional omissions.
