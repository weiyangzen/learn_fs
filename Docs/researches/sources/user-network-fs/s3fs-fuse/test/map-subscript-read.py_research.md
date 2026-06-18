# sources/user-network-fs/s3fs-fuse/test/map-subscript-read.py

## Purpose
Cppcheck addon that flags read-side uses of `std::map::operator[]` and `std::unordered_map::operator[]`, where reads can accidentally insert default values.

## Important APIs, Types, And Control Flow
Imports `cppcheckdata`, defines `reportError`, `simpleMatch`, and `check_map_subscript`. The checker iterates configurations and token lists, finds `[` AST nodes with both operands, skips assignment LHS uses, resolves the container variable, and reports style diagnostics when the type token matches `std :: map <` or `std :: unordered_map <`. The script loads each dump argument and exits with cppcheck’s addon exit code.

## State And Persistence
Reads cppcheck dump files and emits diagnostics through cppcheck’s reporting API. No repository files are mutated.

## Dependencies And Integration Points
Depends on cppcheck addon Python APIs and dump generation (`cppcheck --dump`). It integrates with static analysis workflows to enforce safer map lookup patterns.

## Risks And Test Signals
Pattern matching is token-shape sensitive and may miss aliases, typedefs, namespace variations, references, or complex expressions. It can false-positive on deliberate insertion-through-read idioms not written as assignment LHS. Test signals are cppcheck addon runs over representative C++ snippets.
