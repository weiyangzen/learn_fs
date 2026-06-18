# sources/security-integrity/selinux/libsepol/cil/src/cil_fqn.c

## Purpose
`cil_fqn.c` manages fully qualified names for CIL symbol-table data. It constructs FQNs from lexical scopes, compares datum names in sorted order, and recursively assigns FQNs through AST scopes.

## Important APIs, Types, And Functions
The public functions are `cil_fqn_qualify_blocks`, `cil_fqn_qualify`, `cil_fqn_qualify_all`, and `cil_fqn_compare`. `cil_fqn_qualify_blocks` joins a datum name with a list of containing block names using dots. `cil_fqn_qualify` builds the containing block list by walking datum node parents. `cil_fqn_qualify_all` walks an AST and qualifies every symbol datum in block, macro, or conditional scopes.

## Control Flow
Qualification starts at a datum node and climbs through parent AST nodes, collecting non-root block names. It then builds a dot-separated string and interns it through the string pool. The AST-wide pass skips no scopes; it checks node flavors that own symbol tables and maps every symtab datum through the qualifier callback.

## State And Persistence Behavior
The module mutates `struct cil_symtab_datum::fqn` pointers. FQNs are interned in the CIL string pool, so lifetime is tied to the process/database string pool rather than the caller. It does not write files.

## Dependencies And Integration Points
It uses `cil_list` for temporary block-name stacks, `cil_symtab_map` to visit scoped symbols, `cil_strpool_add` for stable string storage, and `cil_tree` parent links. Build and verify phases rely on FQNs for logging, sorting, matching, and output.

## Risks And Edge Cases
The code assumes every datum has at least one AST node and meaningful parent links. Scope qualification must avoid root names while preserving block nesting. Name length allocation is computed before formatting; off-by-one or missing separators would corrupt generated FQNs.

## Test Signals
Tests should build nested block/macro policies and assert qualified names, especially same local names in different blocks. Sorting tests for `cil_fqn_compare` and diagnostic tests that include FQNs are useful integration signals.
