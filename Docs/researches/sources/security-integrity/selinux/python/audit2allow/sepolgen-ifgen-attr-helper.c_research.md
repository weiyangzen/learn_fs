<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/selinux/python/audit2allow/sepolgen-ifgen-attr-helper.c -->
# sources/security-integrity/selinux/python/audit2allow/sepolgen-ifgen-attr-helper.c

## Purpose
Reads a binary SELinux policy and emits attribute access vectors in the format consumed by `sepolgen-ifgen`.

## Important APIs, Types, And Functions
Important local types/functions are `struct val_to_name`, `perm_name()`, `render_access_mask()`, `render_key()`, `struct callback_data`, `output_avrule()`, `attribute_callback()`, `load_policy()`, `usage()`, and `main()`. It uses libsepol `policydb_t`, `policy_file`, `policydb_read`, hashtab and avtab traversal, plus libselinux policy path discovery.

## Control Flow
`main()` validates `out_file [policy_file]`, loads the requested, current, or version-suffixed default binary policy, opens the output, then maps all policy types. For each `TYPE_ATTRIB`, `attribute_callback()` writes an attribute header and scans both unconditional and conditional TE avtabs. `output_avrule()` filters allowed AV rules with the attribute as source, renders source/target/class names and permission names, and writes comma-separated rows.

## State And Persistence
It writes the helper output file. It reads binary policy files and allocates/destroys a full policydb.

## Dependencies And Integration Points
It is a companion binary for the Python `sepolgen-ifgen` script and depends on libsepol's internal policydb structures.

## Risks And Edge Cases
The permission variable is not reset inside each permission-bit iteration, so stale names are a possible correctness risk if a lookup fails after a previous success. Internal libsepol structure assumptions can break with ABI changes. `load_policy(argv[2])` is unsafe when `argc == 2` because it passes an out-of-bounds argument instead of NULL.

## Test Signals
Tests should invoke with explicit and implicit policy paths, compare known attribute output for dummy policy, run under ASan/UBSan for argv and stale-pointer issues, and verify malformed policy failure cleanup.
<!-- END_FILE_RESEARCH: sources/security-integrity/selinux/python/audit2allow/sepolgen-ifgen-attr-helper.c -->
