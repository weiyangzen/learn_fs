# sources/user-network-fs/samba/source4/dsdb/samdb/ldb_modules/anr.c

## Purpose
`anr.c` implements the LDB module for Active Directory ambiguous name resolution. It rewrites searches containing the pseudo-attribute `anr` into an OR filter over schema attributes marked with `SEARCH_FLAG_ANR`, with AD-compatible handling for exact-match syntax and split given-name/surname searches.

## Important APIs, types, and functions
- `make_parse_list()` creates two-arm `LDB_OP_AND` or `LDB_OP_OR` parse tree nodes and steals both child arms.
- `make_match_tree()` creates equality or prefix-substring match parse tree nodes for a real attribute and match value.
- `anr_replace_value()` expands one `anr` value into a tree over all schema ANR attributes and optional `givenName`/`sn` split filters.
- `anr_replace_subtrees()` recursively replaces eligible `anr` equality or prefix-substring subtrees inside the copied filter tree.
- `parse_tree_anr_present()` detects any operation that references `anr` before paying rewrite costs.
- `anr_search()` is the module search hook: detect, shallow-copy the parse tree, rewrite, build a downstream search, and forward replies through `anr_search_callback()`.

Key local structs are `anr_context` for the downstream request/callback and `anr_present_ctx` for detection.

## Control flow
The search hook first walks the original parse tree looking for any `anr` reference across equality, comparison, substring, present, and extended operations. If none is found, it passes the request unchanged. If ANR is present, it copies the parse tree, recursively replaces only equality or simple prefix-substring forms of `anr`, and submits a new search request with the expanded tree and original base/scope/attrs/controls.

`anr_replace_value()` obtains the current schema and iterates every schema attribute. Attributes with `SEARCH_FLAG_ANR` become either `(attr=value)` when the input value starts with `=` or `(attr=value*)` otherwise. These are chained as nested OR nodes. If the search value contains a space, it also adds `(|(&(givenName=first)(sn=second))(&(sn=first)(givenName=second)))` using the same equality-or-prefix mode. The callback transparently forwards entries, referrals, and done/error replies to the original request.

## State and persistence behavior
The module is stateless and makes no persistent changes. It allocates a rewritten parse tree under the per-request context, steals values/children into that tree, and frees everything with the request. The original caller parse tree is shallow-copied before modification to avoid mutating caller-owned memory.

## Dependencies and integration points
It depends on LDB parse tree APIs, DSDB schema access, schema `searchFlags`, `SEARCH_FLAG_ANR`, and the LDB module stack. It integrates as module `"anr"` via `ldb_anr_module_init()`.

## Risks and edge cases
- Only equality and simple prefix-substring `anr` filters are expanded; present/comparison/extended uses are detected but not transformed by `anr_replace_subtrees()`.
- If no schema is available, ANR rewriting fails with operations error.
- The prefix-substring expansion reuses a single `ldb_val` pointer across multiple match tree chunks; lifetime is tied to the copied tree/request context.
- Split-name logic only splits on the first ASCII space and hardcodes `givenName`/`sn` in addition to schema-marked ANR attributes.
- Nested OR construction can produce deep trees for many ANR attributes.

## Test signals
Useful tests include `(anr=foo)` prefix expansion, `(anr==foo)` exact expansion, substring `anr=foo*`, filters without ANR passing unchanged, compound AND/OR/NOT replacement, split names like `Jane Smith`, schema without ANR attributes, missing schema failure, and callback forwarding of entries/referrals/done/error.
