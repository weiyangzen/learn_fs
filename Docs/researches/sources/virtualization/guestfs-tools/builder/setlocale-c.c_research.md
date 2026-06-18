# File Research: sources/virtualization/guestfs-tools/builder/setlocale-c.c

## Scope

OCaml C stub exposing `setlocale` for virt-builder.

## Behavior

- Maps OCaml category indexes to `LC_ALL`, `LC_CTYPE`, `LC_NUMERIC`, `LC_TIME`, `LC_COLLATE`, `LC_MONETARY`, and `LC_MESSAGES`.
- Accepts an OCaml optional locale string; `None` maps to `NULL`.
- Calls C `setlocale`.
- Returns `Some locale_string` on success or `None` on failure.

## Risks And Invariants

- The OCaml-side enum ordering must match `lc_string_table`.
- Returned `setlocale` storage is copied immediately into an OCaml string.
