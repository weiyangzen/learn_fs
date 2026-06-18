# sources/security-integrity/selinux/libsepol/cil/src/cil_flavor.h

## Purpose
`cil_flavor.h` defines the central `enum cil_flavor` used as the runtime tag for parse tree nodes, AST nodes, list items, operators, and declarative CIL objects.

## Important APIs, Types, And Functions
The file defines two offset constants, `CIL_MIN_OP_OPERANDS` and `CIL_MIN_DECLARATIVE`, and a single enum. Early values represent structural nodes and post-parse statement nodes. Operator values include `CIL_ALL`, `CIL_AND`, `CIL_OR`, `CIL_XOR`, `CIL_NOT`, `CIL_EQ`, `CIL_NEQ`, `CIL_RANGE`, constraint relation operators, and constraint operands. Declarative values include blocks, macros, booleans, classes, permissions, users, roles, types, MLS objects, contexts, IP addresses, policy capabilities, and permissionx.

## Control Flow
There is no executable control flow. The numeric layout lets code distinguish structural, operator, and declarative categories by ranges.

## State And Persistence Behavior
The enum values become in-memory tags for almost every CIL object and list item. They are not directly persisted, but they influence AST destruction, symbol-table routing, verification, and policy generation.

## Dependencies And Integration Points
Nearly every CIL source file includes this header directly or through `cil_internal.h`. `FLAVOR()`-style datum inspection, switch statements, list traversal, symbol-table mapping, parser/build phases, and post-processing all depend on these stable tags.

## Risks And Edge Cases
Changing enum values can break assumptions in switch statements and range checks. Adding a new CIL construct requires updates across parser/build, verification, destruction, policy generation, binary generation, and research helpers. Operator tags are stored through `void *` casts in lists, so pointer-width-safe casts must be used by implementation code.

## Test Signals
Build failures reveal missing switch cases only where compilers warn. Better signals are parsing and compiling policies that exercise every flavor class, plus sanitizer runs through AST destruction and policy generation after adding or changing a flavor.
