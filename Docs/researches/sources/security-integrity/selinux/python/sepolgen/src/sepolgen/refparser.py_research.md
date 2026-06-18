# sources/security-integrity/selinux/python/sepolgen/src/sepolgen/refparser.py

## Purpose
This file implements the PLY lexer and yacc grammar for SELinux reference-policy language: core policy statements plus refpolicy/M4 constructs such as `interface`, `template`, `optional_policy`, `tunable_policy`, `ifdef`, `ifelse`, `define`, and `gen_require`. It produces the AST classes from `refpolicy.py`.

## Important APIs, Types, And Functions
The lexer defines punctuation, identifiers, paths, filenames, IPv6 addresses, numbers, and reserved words for modules, object contexts, types, roles, AV rules, type rules, booleans, and refpolicy macros. It ignores whitespace, comments, `dnl`, and `refpolicywarn`.

Parser globals are `m`, `error`, `parse_file`, `spt`, `success`, `parser`, and `lexer`. `collect()` attaches parsed children to parent nodes, optionally tagging conditional branch values. `expand()` expands permission macros through `SupportMacros`. Grammar functions create `ModuleDeclaration`, `Interface`, `Template`, `OptionalPolicy`, `TunablePolicy`, `IfDef`, `IfElse`, `InterfaceCall`, `ObjPermSet`, `SecurityContext`, filesystem/network context nodes, `Type`, `Role`, `AVRule`, `TypeRule`, `TypeBound`, booleans, attributes, and other refpolicy nodes.

Public functions are `create_globals()`, `parse(text, module=None, support=None, debug=False)`, `list_headers(root)`, and `parse_headers(root, output=None, expand=True, debug=False)`.

## Control Flow
`parse()` initializes or reuses global lexer/parser objects, resets line/success state, parses text into a provided or new module, and rebuilds parser globals after failures. `parse_headers()` discovers `.if`, selected `.spt`, and pattern files, parses support macros first, injects a synthetic `can_exec` interface, then parses each module file into `Headers.children`, optionally showing a progress bar.

## State And Persistence Behavior
Parser state is global and reused across calls until failure. The AST is in-memory; parse functions append children to caller-provided modules or a fresh module. Header parsing reads policy files but writes no files. Support macro expansion depends on global `spt`.

## Dependencies And Integration Points
It depends on bundled `lex.py`, bundled `yacc`, `access.AccessVector`, `defaults.headers()`, and `refpolicy` AST classes. Its output feeds `interfaces`, `matching`, `policygen`, and `output`.

## Risks And Edge Cases
The grammar intentionally ignores `require`, permissive, range transition, and role transition semantics. Several productions appear bug-prone: `p_devicetreecon` references `refpolicy.DevicetTeeCon()` instead of `DeviceTreeCon`; some range concatenations use the wrong token index; `p_names()` has an `expand([p[1]])` call missing the destination set. `p_error()` assumes `tok` is not `None`, so EOF syntax errors may fail differently. Global parser state is not thread-safe. Path, filename, IPv6, and context regexes are narrow and may reject valid policy text.

## Test Signals
Tests should parse representative `.if`, `.spt`, and `.te` snippets for every emitted AST type; verify support macro expansion; cover optional/tunable true/false branches; confirm parser rebuild after syntax failure; exercise comments/refpolicywarn handling; and include regression tests for devicetreecon, type/role transitions, ranges, EOF errors, quoted filenames, IPv6 nodecon, and names with complements.
