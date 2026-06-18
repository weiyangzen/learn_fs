# sources/security-integrity/selinux/libsepol/cil/src/cil_symtab.c

## Purpose

`cil_symtab.c` wraps libsepol symbol tables for CIL datums and implements a small complex-key symbol table used for duplicate/collision checks over multi-field rule keys.

## Important APIs, Types, and Functions

Basic datum APIs are `cil_symtab_init()`, `cil_symtab_datum_init()`, `cil_symtab_datum_destroy()`, `cil_symtab_insert()`, `cil_symtab_remove_datum()`, `cil_symtab_get_datum()`, `cil_symtab_map()`, and `cil_symtab_destroy()`. Complex-key APIs are `cil_complex_symtab_init()`, `cil_complex_symtab_insert()`, `cil_complex_symtab_search()`, and `cil_complex_symtab_destroy()`.

## Control Flow

Normal insertion delegates to `hashtab_insert()`. On success it sets datum `name`, `fqn`, owner `symtab`, increments `nprim`, and optionally records the AST node in `datum->nodes`. Removal deletes by `datum->name`, decrements `nprim`, and clears owner state. Destroy clears each datum's `symtab` back-pointer before destroying the underlying hashtab. Complex symtab insertion hashes four integer keys, keeps bucket lists sorted by key fields, rejects exact duplicates with `SEPOL_EEXIST`, and otherwise links a new node.

## State and Persistence Behavior

`struct cil_symtab_datum` owns a list of AST nodes referencing the declaration but not the symtab itself. `cil_symtab_datum_remove_node()` removes a node reference and destroys the datum if no nodes remain. Complex symtab nodes own only the wrapper node allocation; keys and datum payloads are external.

## Dependencies and Integration Points

The file depends on libsepol `symtab_t`/`hashtab_t`, CIL list/tree structures, memory helpers, string pool conventions, and logging. Resolver name lookup and tree destruction both rely on datum back-pointers and node lists being maintained correctly.

## Risks and Test Signals

Failure paths call `exit(1)` for allocation/symtab creation failures, so callers cannot recover. `cil_symtab_remove_datum()` assumes `datum->symtab` and `datum->name` are coherent. Complex symtab hashing assumes `nslots` is a power of two because `mask = size - 1`. Tests should cover duplicate insert, node-list removal and datum destruction, temporary remove/reinsert during macro argument resolution, map iteration, and complex-key search early-exit ordering.
