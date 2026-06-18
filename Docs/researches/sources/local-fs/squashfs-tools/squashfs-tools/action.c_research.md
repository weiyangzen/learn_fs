# File Research: sources/local-fs/squashfs-tools/squashfs-tools/action.c

Implements the `mksquashfs` action language: parsing, expression evaluation, test predicates, action dispatch, xattr rule evaluation, move scheduling, symlink dereference tests, and action-file reading.

Core parser behavior:
- `read_file()` reads action files line-by-line, supports `\` continuations, skips blank lines and `#` comments, and enforces `MAX_LINE` chunks.
- `get_token()` tokenizes punctuation/operators and quoted/escaped strings.
- `parse_expr()` parses left-associative `&&`/`||`, unary `!`, parenthesized subexpressions, and test atoms.
- `parse_action()` parses `action(args)@expr`, validates action name/argument count, calls action-specific argument parsing, then appends the action to the relevant global list.

Action categories maintained as global arrays:
- Fragment placement: `fragment`, plus defaults/tail fragments.
- Exclusion/pruning: `exclude`, `prune`, `empty`.
- Symlink handling: `dereference`.
- Metadata rewrites: `uid`, `gid`, `guid`, `mode`/`chmod`, fragment/compression flags, `align`, `noop`.
- Tree rewrite: `move`.
- Xattr filtering/injection: `xattrs-exclude`, `xattrs-include`, `xattrs-add`.

Evaluation behavior:
- `eval_expr()` short-circuits logical operations.
- Verbose action logging records expression evaluation and prints via `progressbar_info()` only for selected true/false outcomes.
- `file_type_match()` restricts tests/actions to regular files, directories, symlinks, or all supported filesystem object types.
- Public evaluators build `struct action_data` from `dir_ent`, pathname/subpathname, stat buffer, root, and depth.

Move action behavior:
- Move actions are first evaluated into `move_ent` records rather than immediately mutating the tree.
- Multiple compatible move actions may merge rename and destination changes.
- Conflicting renames/destinations and moves into self-subdirectories are reported.
- `do_move_actions()` applies queued moves after scanning and rechecks destination conflicts.

Xattr behavior:
- Include/exclude actions compile POSIX extended regexes.
- Matching actions produce linked lists of regex rules for later xattr filtering.
- `xattrs-add` delegates parsing to `xattr_parse()` and returns matched `struct xattr_add` records.

Supported tests include:
- Name/path matching: `name`, `pathname`, `subpathname`.
- Numeric comparisons and ranges for size, tailsize, inode, blocks, uid/gid, nlink, depth, dircount.
- User/group lookup by name.
- File type, true/false, permission expressions.
- External `file(1)` regex test and shell `exec` test.
- Symlink tests: `exists`, `absolute`, `stat(expr)`, `readlink(expr)`.
- Contextual `eval(path, expr)` over another output-tree entry.

Notable risks/quirks:
- `file_fn()` forks `file -b` and treats command failure as fatal via `BAD_ERROR`.
- `exec_fn()` executes `/bin/sh -c` with file path context in environment variables.
- Many parser allocations are intentionally process-lifetime; failed parse paths free only some intermediate arrays.
- `error.h` fatal macros are used for internal invariants, so some filesystem/action errors terminate the whole process.
