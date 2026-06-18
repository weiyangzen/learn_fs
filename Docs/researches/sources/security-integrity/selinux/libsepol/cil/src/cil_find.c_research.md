# sources/security-integrity/selinux/libsepol/cil/src/cil_find.c

## Purpose
`cil_find.c` implements rule-intersection search over the resolved CIL AST. Its main job is finding AV rules that overlap a target AV rule, including SELinux-specific source/target matching involving type attributes and `self`, `notself`, and `other`.

## Important APIs, Types, And Functions
The public functions are `cil_find_matching_avrule_in_ast` and `cil_expand_class`. Important private helpers include `cil_type_match_any`, `cil_type_matches`, `cil_self_match_any`, `cil_notself_match_any`, `cil_other_match_any`, `cil_notself_other_match_any`, classperms match helpers, `cil_permissionx_match_any`, and `cil_find_matching_avrule`.

`struct cil_args_find` carries traversal parameters: requested node flavor, target rule, output list, and whether the target can match itself.

## Control Flow
`cil_find_matching_avrule_in_ast` walks from a caller-supplied AST node. The walker skips abstract blocks and macros, examines only `CIL_AVRULE` or `CIL_AVRULEX` nodes matching the requested flavor, and delegates to `cil_find_matching_avrule`.

Rule matching checks rule kind, extended-rule flag, source type overlap, target type overlap, and permission overlap. Target matching has separate branches for `self`, `notself`, and `other`; some cases are deliberately false because self cannot match notself/other. For ordinary AV rules it recursively compares classperms lists; for extended AV rules it compares permissionx kind, permission bitmap overlap, and expanded object classes.

## State And Persistence Behavior
The module does not mutate persistent state. It allocates temporary lists from `cil_expand_class`, temporary ebitmaps during type matching, appends matching AST nodes to the caller-owned output list, and destroys its own temporaries.

## Dependencies And Integration Points
It depends on libsepol `ebitmap`, `cil_list`, `cil_tree_walk`, `cil_symtab_map`, and CIL internal structs. `cil_deny.c` uses it to find allow rules affected by deny rules. `cil_binary.c` uses it for neverallow-style matching checks during binary policy generation.

## Risks And Edge Cases
Matching semantics are subtle for attributes with multiple concrete types and for pseudo-targets. An error can either miss a real overlap or report a false conflict. Map classes require expansion through map permissions, and extended permissions require both object-class and bitmap overlap. Empty attributes and degenerate `notself`/`other` cases need careful coverage.

## Test Signals
Tests should cover concrete type versus concrete type, attribute versus concrete type, attribute versus attribute, special target combinations, map classes, classpermission sets, and permissionx ranges. Integration signals are deny-rule rewrites and neverallow diagnostics matching expected source locations.
