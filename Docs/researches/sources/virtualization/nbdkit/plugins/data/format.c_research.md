# File Research: sources/virtualization/nbdkit/plugins/data/format.c

Parser, optimizer, and evaluator for the data plugin’s `data="..."` mini-language.

Supported expression types:
- Null/list expressions.
- Literal bytes.
- Absolute, relative, and alignment offsets: `@N`, `@+N`, `@-N`, `@^ALIGN`.
- File inclusion: `<FILE`.
- Script output inclusion: `<(SCRIPT)` on non-Windows.
- C-like strings.
- Repeated/fill data: `expr*N`.
- Named expressions and assignment: `expr -> \name`, `\name`.
- Slices: `expr[N:M]`.
- Endian words: `le16:`, `le32:`, `le64:`, `be16:`, `be32:`, `be64:`.
- Inline `base64:...`.
- `$VAR` expansion from extra plugin parameters or environment variables.
- Comments starting with `#`.

Architecture:
- Parses to a global AST table addressed by `node_id`, avoiding pointer/reference lifetime complexity.
- Uses a null node at index 0 for common empty expressions.
- Has GCC-only macro checks to type-check internal `expr(...)` construction calls.
- `read_data_format` parses, optimizes, optionally prints AST debug output, evaluates into an allocator, then frees the AST table.

Optimization pass:
- Removes null list entries.
- Flattens safe lists.
- Combines adjacent constants into strings or fills.
- Collapses `expr*0`, `expr*1`, nested repeats, fill repeats, small string repeats, and single-byte repeats.
- Slices constant strings/fills/bytes/nulls when possible.
- Avoids flattening scoped expressions such as offsets, names, and assignments.

Evaluator:
- Writes bytes, strings, fills, files, scripts, slices, repeats, and nested lists into an allocator.
- Tracks current offset and maximum observed size.
- Evaluates named expressions in the dictionary environment captured when assigned.
- Optimizes `<FILE[N:M]` and `<(SCRIPT)[:LEN]` to avoid reading unbounded input.
- Uses temporary sparse allocators for nested/repeated/sliced expressions.

Platform behavior:
- Script expressions use `popen` on non-Windows.
- Windows reports script expressions as unsupported.

Notable constraints:
- Alignment offsets require power-of-two alignment.
- Numeric/unicode string escape sequences other than `\xNN` are not implemented.
- Some overflow checks are explicit, while some offset arithmetic has comments noting future checks.
