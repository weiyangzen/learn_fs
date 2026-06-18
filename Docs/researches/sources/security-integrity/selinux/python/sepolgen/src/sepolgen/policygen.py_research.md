# sources/security-integrity/selinux/python/sepolgen/src/sepolgen/policygen.py

## Purpose
This module generates SELinux reference-policy modules from access vectors. It can emit raw allow/dontaudit rules, extended permission rules, require blocks, interface calls, role/type associations, and explanatory comments from audit messages.

## Important APIs, Types, And Functions
Constants `NO_EXPLANATION`, `SHORT_EXPLANATION`, and `LONG_EXPLANATION` control comment detail. `PolicyGenerator` owns the target `refpolicy.Module`, generation flags (`ifgen`, `gen_requires`, `dontaudit`, `xperms`, `gen_cil`), and comment style. Configuration methods enable reference-policy interface generation, require generation, explanations, dontaudit output, xperm generation, and CIL comments. `set_module_name()` creates or updates a `ModuleDeclaration`; `get_module()` optionally calls `gen_requires()`.

Private `__add_av_rule()` converts one access vector to `refpolicy.AVRule`, adds audit explanations and audit2why/setools hints, and appends it. `__add_ext_av_rules()` creates `AVExtRule` children for `av.xperms`. `add_access()` optionally routes vectors through `InterfaceGenerator`. `add_role_types()` appends role-type rules.

`explain_access()` formats short or long audit-message comments and interface alternatives. `call_interface()` maps interface parameter metadata to access-vector fields. `InterfaceGenerator` disables unsupported interfaces, finds matches through `matching.AccessMatcher`, deduplicates generated interface calls, and returns raw vectors plus calls. `gen_requires()` synthesizes `Require` nodes from rules, interface-call args, and role types.

## Control Flow
Generation usually configures a `PolicyGenerator`, sets a module name, calls `add_access()` with an access-vector set, optionally adds role types, then calls `get_module()` and `output.ModuleWriter.write()`. With interface generation enabled, matching runs before raw rule emission; matched accesses become interface calls and unmatched accesses become AV rules.

## State And Persistence Behavior
The generator mutates a `refpolicy.Module` in memory by appending child nodes and inserting requires at node starts. `InterfaceGenerator.calls` accumulates matches across `gen()` calls, so reuse can carry previous matches unless a new generator is created. `PolicyGenerator.domains` lazily caches `setools.seinfo()` results for write diagnostics. No files are written directly.

## Dependencies And Integration Points
It depends on `selinux.audit2why`, optional `setools` symbols (`seinfo`, `sesearch`, constants), `refpolicy`, `objectmodel`, `access`, `interfaces`, `matching`, and `util`. It sits between audit/access parsing and final formatting by `output.py`.

## Risks And Edge Cases
The optional `setools` import silently fails, and broad `except` blocks suppress diagnostics. Interface support is intentionally limited to positional source, target, and object-class parameters; roles and more complex signatures are disabled. `gen_requires()` is noted as untested with nesting and may add duplicate or empty requires. Explanations assume audit messages expose specific fields. Comment generation differs for CIL and policy syntax. Reusing `InterfaceGenerator` may duplicate old call matches.

## Test Signals
Tests should cover raw allow and dontaudit generation, xperm emission, CIL comment prefixes, module declaration style with and without interfaces, short/long explanations, audit2why ALLOW/DONTAUDIT/BOOLEAN/CONSTRAINT comments, interface matching and deduplication, unsupported interface disabling, require synthesis, and behavior when setools is absent.
