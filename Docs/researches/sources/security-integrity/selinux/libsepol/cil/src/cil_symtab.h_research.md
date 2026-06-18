# sources/security-integrity/selinux/libsepol/cil/src/cil_symtab.h

## Purpose

`cil_symtab.h` defines the CIL datum wrapper around libsepol symbol tables and the complex-key table types used by verification logic.

## Important APIs, Types, and Functions

`struct cil_symtab_datum` contains declaration nodes, simple name, fully qualified name, and owner symtab. Convenience macros `DATUM()`, `NODE()`, and `FLAVOR()` cast datums to their primary AST node/flavor. Complex-key types store four `intptr_t` keys, a payload wrapper, bucket nodes, and table metadata. The header declares all normal and complex symtab operations.

## Control Flow and Integration

Resolvers use the normal symtab API for scoped lookup and insertion. Tree destruction uses datum node lists to decide whether declaration payloads can be freed. Verifier code can use the complex symtab for multi-field duplicate detection, though some rule duplicate checks are currently disabled in comments.

## State, Dependencies, and Risks

The macros assume each datum has at least one node and that the first node is representative. That is invalid for partially initialized or already-destroyed datums. Complex-key structures do not own key payloads, so callers must manage key lifetime. The header depends on libsepol symtab/hashtab headers and `cil_tree.h`.

## Test Signals

Tests should cover macro behavior for datums with multiple nodes, compile inclusion order, complex symtab initialization with power-of-two slot counts, and destruction after partial insertion.
