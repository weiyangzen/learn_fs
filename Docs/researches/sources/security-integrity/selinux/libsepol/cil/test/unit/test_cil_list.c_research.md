# sources/security-integrity/selinux/libsepol/cil/test/unit/test_cil_list.c

## Purpose
This file tests CIL list initialization plus append and prepend behavior for `struct cil_list` and `struct cil_list_item`. It emphasizes status-code handling for valid insertions and null or malformed arguments.

## Important APIs, Types, And Functions
It includes `CuTest.h`, `CilTest.h`, `cil_internal.h`, and `cil_build_ast.h`. Test targets include `cil_list_init`, `cil_list_item_init`, `cil_list_append_item`, and `cil_list_prepend_item`. The tests use `struct cil_list`, `struct cil_list_item`, `struct cil_avrule`, `struct cil_classpermset`, `struct cil_permset`, `struct cil_tree`, `struct cil_tree_node`, and `struct cil_db`.

## Control Flow
`test_cil_list_init` allocates an AV rule, initializes nested class/permission structures, initializes the permissions list, asserts it is non-null, and destroys the AV rule. Append/prepend tests generate a small `mlsconstrain` parse tree, initialize DB and AST node context, create list items pointing at class tokens in the parse tree, and call append or prepend. Negative tests pass a null list, null item, or a list item that already has `next` set and assert `SEPOL_ERR`.

## State And Persistence
All list state is heap allocated and in memory. The tested state transitions are head/tail insertion and rejection of invalid inputs. The code does not persist data and does not comprehensively free every object in each test, so process lifetime absorbs many allocations.

## Dependencies And Integration Points
The file depends on parser-test helpers to create parse tree data used as list item payloads. It tests utility list functions used broadly by CIL builders, copy logic, expression stacks, and permission/class collections.

## Risks
The tests mostly assert return codes, not exact list ordering, tail links, length, or ownership after operations. `test_cil_list_prepend_item_prepend` only prepends once despite the name. There is no explicit test for append after prepend, empty-list tail consistency, or destroy behavior.

## Test Signals
Good signals include success paths for one and multiple appends, basic prepend success, rejection of null list/item arguments, and rejection of prepending an already-linked item.
