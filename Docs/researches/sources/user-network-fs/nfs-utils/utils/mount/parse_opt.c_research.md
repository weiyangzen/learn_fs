<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-utils/utils/mount/parse_opt.c -->
# sources/user-network-fs/nfs-utils/utils/mount/parse_opt.c

## Purpose

`parse_opt.c` implements the text mount-option list used by `mount.nfs` and `umount.nfs`. It turns comma-delimited option strings into a mutable doubly linked list, preserving option order so callers can model Linux mount parsing rules where the rightmost duplicate wins.

## Important APIs, types, and functions

The private `struct mount_option` stores `keyword`, optional `value`, and list links. `struct mount_options` stores `head`, `tail`, and `count`. Public operations include `po_split`, `po_dup`, `po_replace`, `po_join`, insertion/appending, `po_contains`, `po_contains_prefix`, `po_get`, `po_get_numeric`, `po_rightmost`, `po_remove_all`, and `po_destroy`.

## Control flow

`po_split` creates an empty list, tokenizes on commas with `token.c`, converts each token into `keyword[=value]`, and appends it. Mutators add or delete nodes while keeping head/tail/count correct. Lookup helpers scan either from the head for existence or from the tail for effective values. `po_join` first computes the exact output length, then concatenates each option back into a comma string.

## State and persistence behavior

All state is heap memory owned by a `struct mount_options` handle. `po_replace` transfers list node ownership from source to target and empties the source. The module performs no persistent I/O; its output string is later passed to `mount(2)` or written into mtab-style records by higher layers.

## Dependencies and integration points

It depends on `token.c` for quote-aware tokenization and is used heavily by `stropts.c`, `utils.c`, and network option helpers. It exposes an opaque handle in `parse_opt.h`, allowing mount code to rewrite options without string surgery.

## Risks and edge cases

Quoted commas are handled only at token boundaries; `option_create` itself splits on the first `=` without quote awareness. `po_get_numeric` with `strtol` accepts numeric prefixes because it checks `endptr != option` but not `*endptr == '\0'`. Allocation failures unwind through destroy paths, but callers must honor `PO_FAILED` and `NULL` returns.

## Test signals

Useful tests should cover empty and NULL strings, duplicate rightmost selection, quoted comma tokens, missing values, values with additional `=`, removal of all duplicates, numeric bad values, `po_replace` ownership transfer, and round-trip `po_split`/`po_join`.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-utils/utils/mount/parse_opt.c -->
