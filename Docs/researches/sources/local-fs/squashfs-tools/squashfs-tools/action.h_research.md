# File Research: sources/local-fs/squashfs-tools/squashfs-tools/action.h

Public interface and data model for `action.c`.

Defines:
- Lexer token IDs and token table record shape.
- Expression tree node types: binary op, atom/test, unary op.
- Syntax-error reporting macros with source-position context.
- Numeric comparison/range parse structures.
- `struct test_entry` for action-language predicate registry.
- Action IDs and file-type applicability constants.
- Action logging constants for true/false/verbose action diagnostics.
- `struct action_entry`, `struct action_data`, and `struct action`.
- Per-action data structs for uid/gid/guid, empty policy, move queue, xattr regexes, alignment, dereference policy, and permission tests.

External API:
- Parses individual actions and action files.
- Evaluates action classes: fragment, exclude, dereference, empty, move, prune, xattr include/exclude/add, and general metadata actions.
- Exposes counters such as `any_actions()`, `move_actions()`, `xattr_add_actions()`.
- Exposes `do_move_actions()` and `dump_actions()`.

Notable coupling:
- Depends on `struct dir_ent`, `struct dir_info`, `struct inode_info`, and `struct xattr_add` from other mksquashfs internals.
- Declares `read_bytes()` despite its implementation living outside this file group.
