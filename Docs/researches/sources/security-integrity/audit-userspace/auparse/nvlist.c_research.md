<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/audit-userspace/auparse/nvlist.c -->
# sources/security-integrity/audit-userspace/auparse/nvlist.c

## Purpose
Implements dynamic arrays of parsed name/value fields for each audit record and for preloaded interpretation lists.

## Important APIs, types, and functions
Functions include `nvlist_create`, `nvlist_next`, `nvlist_append`, `nvlist_interp_fixup`, `nvlist_goto_rec`, `nvlist_find_name`, `nvlist_get_cur_type`, `nvlist_interp_cur_val`, and `nvlist_clear`. `alloc_array` starts with `NFIELDS` entries and append doubles capacity.

## Control flow
Creation initializes fields and allocates the first array. Append validates name/value pointers, expands as needed, copies pointers into the next slot, makes it current, and increments count. Interpretation is lazy: `nvlist_interp_cur_val` returns cached `interp_val` or calls `do_interpret`. Clear releases interpreted values, optionally frees duplicated fields outside the original record buffer, frees the record buffer and array, and resets counters.

## State and persistence behavior
State is per `nvlist`: array, current index, count, capacity, original parsed record buffer, and end pointer. Field name/value pointers often alias the record buffer, so `not_in_rec_buf` protects against freeing non-owned memory.

## Dependencies and integration points
Depends on `rnode.h`, `interpret.h`, and `auparse-idata.h`. `rnode.nv` stores parsed record fields, and `interpret.c` also uses `nvlist` to hold auditd-supplied interpretations.

## Risks and test signals
Risks include ownership mistakes for aliased versus duplicated strings, ASAN pointer-pair concerns in `not_in_rec_buf`, `NEVER_LOADED` sentinel interaction, and realloc growth failures. Tests should cover parsing more than `NFIELDS`, lazy interpretation caching, find from current cursor, clear with and without `free_interp`, and interpretation-list fixups.
<!-- END_FILE_RESEARCH: sources/security-integrity/audit-userspace/auparse/nvlist.c -->
