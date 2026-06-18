# sources/security-integrity/selinux/python/sepolgen/src/sepolgen/interfaces.py

## Purpose
This module models SELinux reference-policy interfaces and templates as access-vector summaries. It extracts parameter types, expands nested interface calls, merges attribute-derived access, and indexes interfaces by target type for later matching and policy generation.

## Important APIs, types, and functions
- `Param` stores an interface parameter name like `$1`, its field type (`SRC_TYPE`, `TGT_TYPE`, `OBJ_CLASS`, `ROLE`, or `DEST_TYPE`), related object classes, and whether it is required.
- `__param_insert()` records inferred parameter usage and reports conflicts, promoting ambiguous source/target parameters to source type for implicitly typed objects.
- `av_extract_params()`, `role_extract_params()`, `type_rule_extract_params()`, and `ifcall_extract_params()` infer parameter roles from access vectors, role statements, type rules, and interface calls.
- `AttributeVector` and `AttributeSet` store attribute-to-access summaries and can load them from a bracketed flat file format.
- `InterfaceVector` summarizes one parsed interface/template, including `enabled`, `name`, `access`, `params`, and expansion state. `from_interface()` consumes refpolicy objects and optional attribute summaries.
- `InterfaceSet` stores all vectors, serializes/deserializes them with `to_file()`/`from_file()`, builds target-type indexes, adds headers, maps parameters through calls, and expands nested calls.

## Control flow
`InterfaceVector.from_interface()` iterates parsed interface AV rules, keeps only allow rules, skips suspicious allow rules in `dontaudit`-named interfaces, expands each AV rule into `AccessVector` instances, and adds them while extracting parameter metadata. It then folds in typeattribute-derived access by replacing attribute names with concrete types. Finally it scans roles, type rules, and nested interface calls for additional parameter usage.

`InterfaceSet.add_headers()` adds every interface and template from a parsed headers object, expands nested interface calls, and builds indexes. Expansion is depth-first: `do_expand_ifcalls()` starts at one interface, walks called interfaces/templates through a stack, maps `$N` parameters to actual call arguments with `map_param()`, and adds the called interface's access to the caller vector with `map_add_av()`. Circular self-calls are detected only when a direct call targets the original interface name.

## State and persistence behavior
Most state is in-memory: dictionaries of interfaces, target-type indexes, and expanded access vectors. `to_file()` and `from_file()` support persistence through a plain text format with `[InterfaceVector ...]` headers and comma-joined access-vector rows. `AttributeSet.from_file()` reads a similar format for attributes. No writes occur except through the caller-provided file object in `to_file()`.

## Dependencies and integration points
The module imports `copy`, `itertools`, and local `access`, `refpolicy`, `objectmodel`, `matching`, and `sepolgeni18n._`. `matching` is imported but unused in this file. It depends on parsed refpolicy header objects exposing `interfaces()`, `templates()`, `avrules()`, `roles()`, `typerules()`, `typeattributes()`, and `interface_calls()`. It uses `objectmodel.implicitly_typed_objects` to resolve source/target parameter ambiguity.

## Risks and edge cases
- `InterfaceVector.__init__(..., attributes={})`, `from_interface(..., attributes={})`, and `InterfaceSet.add(..., attributes={})` use mutable default dictionaries. They are not mutated here, but the pattern is risky.
- `InterfaceSet.from_file()` returns `None` from `parse_ifv()` when a header has no params; the following access rows are then ignored because `ifv` is false.
- `AttributeSet.from_file()` and `InterfaceSet.from_file()` index `line[0]` without guarding against blank lines.
- `do_expand_ifcalls()` only checks direct calls back to the root interface. Longer cycles can keep pushing calls until already-expanded markers happen to stop descent, and incomplete expansion ordering can hide some recursive access.
- `map_add_av()` uses one `new_perms` set for all source/target/class combinations. That is efficient for normal mappings but assumes permission parameter expansion is independent of the mapped class.
- Conflicts detected by parameter extraction are silently ignored with `pass`, losing diagnostics that would help explain poor matches.

## Test signals
Tests should cover parameter inference from access vectors/type rules/roles/interface calls, ambiguous implicit object handling, serialization round-trips, target-type indexing, nested interface expansion, optional-parameter dropping, attribute replacement, circular-call detection, blank-line parsing, and direct no-parameter interface loading.
