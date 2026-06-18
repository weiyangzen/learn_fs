# sources/user-network-fs/mergerfs/src/str.cpp

## Purpose
Implements string utility routines used across config parsing, option formatting, path lists, and glob/prefix matching.

## Important APIs, Types, and Functions
Functions include `split`, `split_to_set`, `split_on_null`, `lsplit1`, `rsplit1`, `splitkv`, `join`, `startswith`, `endswith`, `contains`, `replace_all`, `trim*`, `tolower`, `erase`, `nullterminate`, `matches`, and path/list helpers declared in `str.hpp`.

## Control Flow
Most helpers scan `std::string_view` with find/rfind loops, build vectors or sets, and preserve empty fields where appropriate. Matching helpers use standard string comparisons or `fnmatch()`. Mutation helpers edit caller-provided strings in place.

## State and Persistence Behavior
All state is local or caller-owned. No persistent storage is used.

## Dependencies and Integration Points
Depends on STL containers, algorithms, `<fnmatch.h>`, and `str.hpp`. It is a foundational dependency for config, branches, xattr parsing, and policy option handling.

## Risks and Edge Cases
Delimiter handling intentionally returns empty pieces for repeated/trailing delimiters in some functions; callers must know that behavior. Case conversion with `std::tolower` needs unsigned-char care. `fnmatch` semantics differ from simple substring matching.

## Test Signals
Unit tests should cover empty strings, leading/trailing delimiters, null-delimited data, glob patterns, replacement recursion, trim whitespace, and non-ASCII bytes.
