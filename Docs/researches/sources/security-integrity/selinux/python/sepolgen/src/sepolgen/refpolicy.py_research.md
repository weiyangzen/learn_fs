# sources/security-integrity/selinux/python/sepolgen/src/sepolgen/refpolicy.py

## Purpose
This module defines sepolgen's reference-policy AST and string emitters. It represents unprocessed refpolicy/M4 constructs, policy statements, contexts, classes, rules, declarations, comments, support macros, and CIL/policy output variants.

## Important APIs, Types, And Functions
`PolicyBase`, `Node`, and `Leaf` provide parent/comment/CIL fields, child traversal, and string conversion. `walktree()` and `walknode()` traverse ASTs. `IdSet`, `list_to_space_str()`, and `list_to_comma_str()` format SELinux identifier sets. `SecurityContext` parses and emits SELinux contexts, using libselinux translation and MLS defaults.

Core declaration/rule classes include `Type`, `TypeAlias`, `Attribute`, `Attribute_Role`, `TypeAttribute`, `RoleAttribute`, `Role`, `AVRule`, `AVExtRule`, `TypeRule`, `TypeBound`, `RoleAllow`, `RoleType`, `ModuleDeclaration`, and `Bool`. Context classes include `InitialSid`, `GenfsCon`, `FilesystemUse`, `PortCon`, `NodeCon`, `NetifCon`, `PirqCon`, `IomemCon`, `IoportCon`, `PciDeviceCon`, and `DeviceTreeCon`. Refpolicy containers include `Headers`, `Module`, `Interface`, `TunablePolicy`, `Template`, `IfDef`, `IfElse`, `OptionalPolicy`, and `SupportMacros`. `Require`, `ObjPermSet`, `ClassMap`, and `Comment` support generated output and macro expansion. `XpermSet` stores extended permission ranges and complements.

## Control Flow
Parsers and generators instantiate leaf/node classes, populate string fields and `IdSet`s, append them to `children`, then output code through `to_string()` or `output.ModuleWriter`. `walktree()` enables type-filtered views such as `node.avrules()` and `node.interfaces()`. `SupportMacros.by_name()` lazily builds a recursively expanded permission map from child `ObjPermSet`s.

## State And Persistence Behavior
The AST is mutable in memory. `children`, comments, CIL mode, require sets, support-macro maps, xperm ranges, and identifier sets can all change after creation. No persistence occurs directly, but `to_string()` is the serialization boundary used by `output.py`.

## Dependencies And Integration Points
It depends on `selinux` for context translation and MLS checks. It is the central integration point for `refparser` (producer), `policygen` (producer/mutator), `matching` and `interfaces` (consumers of rules and parameters), and `output` (serializer).

## Risks And Edge Cases
Validation is intentionally light: invalid identifiers, mismatched permissions, and M4 `$1` placeholders can live in rules. Several implementation issues are visible: `PolicyBase.__init__` ignores the `parent` argument; `RoleAttribute.to_string()` references `self.type` in CIL mode though the class defines `role`; `Attribute.to_string()` appears to swap CIL/non-CIL strings; `Bool.to_string()` checks `s.state` instead of `self.state`; `InitialSid` defines `__init` rather than `__init__`; some CIL emitters may omit separators/newlines. `walktree(type=...)` filters children before descending, so it can skip descendants under non-matching intermediate nodes.

## Test Signals
Tests should cover string output for every leaf in both policy and CIL modes, `SecurityContext` parsing/default MLS behavior, xperm range normalization and complements, support macro recursive expansion, traversal helpers, require generation strings, comments and comment merging, `InterfaceCall.matches()`, and regression tests for the typo/field issues noted above.
