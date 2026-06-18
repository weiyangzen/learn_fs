# sources/security-integrity/selinux/python/sepolgen/src/sepolgen/objectmodel.py

## Purpose
This module centralizes SELinux object-class and permission knowledge used by policy generation and interface matching. It models permission information-flow direction and relative bandwidth/weight so generic generation logic does not embed object-model details.

## Important APIs, Types, And Functions
`implicitly_typed_objects` lists classes often labeled with the creating process type. Flow constants are `FLOW_NONE`, `FLOW_READ`, `FLOW_WRITE`, and `FLOW_BOTH`, with `str_to_dir` and `dir_to_str` mappings for permission-map files. `PermMap` stores one permission's name, direction, and weight. `PermMappings` stores `classes[obj_class][perm] = PermMap`, defaulting unknown permissions to both-direction flow with weight `5`.

`PermMappings.from_file(fd)` parses Apol/setools-style permission maps with `class` headers and `perm direction weight` rows. `get()` raises on unknown class/permission, `getdefault()` returns defaults, `getdefault_direction()` ORs flow directions for a permission set, and `getdefault_distance()` sums weights.

## Control Flow
Consumers load a permission map once, then scoring code in `matching.py` repeatedly asks for permission weights and flow directions. Parsing is line-oriented and stateful: a `class` row starts a new current class; subsequent rows populate that class until another class row appears.

## State And Persistence Behavior
All state is in-memory. `PermMappings.classes` persists parsed mappings for the object's lifetime. No files are written. Unknown permissions are not cached; every default lookup creates a new `PermMap`.

## Dependencies And Integration Points
`matching.AccessMatcher` uses this module to calculate permission distance and write-flow penalties. `policygen` imports it for generation context. The permission map format is expected to be shipped with sepolgen rather than edited interactively by users.

## Risks And Edge Cases
`from_file()` is deliberately strict and raises `ValueError` on duplicate class declarations, malformed permission rows, or permissions before any class. It treats `fields[0] == "#"` as comments, so inline comments or leading whitespace before comments rely on split behavior. Unknown permissions default to broad both-direction flow, which keeps generation running but can over-penalize or over-allow interface candidates. The module does not validate that directions exist in `str_to_dir` before indexing.

## Test Signals
Tests should cover parsing valid class blocks, skipping blank/comment/single-field lines, duplicate classes, malformed rows, permission-before-class errors, `get` failures, default fallback behavior, combined direction ORing, and distance summation.
