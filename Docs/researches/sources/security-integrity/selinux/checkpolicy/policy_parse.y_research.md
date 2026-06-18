# sources/security-integrity/selinux/checkpolicy/policy_parse.y

## Purpose

`policy_parse.y` is the Bison grammar for SELinux source policies and loadable modules. It defines the parse shape for base policies, module policies, MLS constructs, TE/RBAC rules, constraints, security contexts, network/device contexts, optional blocks, and require blocks. Semantic actions push lexed identifiers into `id_queue` and call `policy_define.c`/`module_compiler.c` functions to mutate `policydbp`.

## Important Grammar Areas

The top-level `policy` can be `base_policy` or `module_policy`. `base_policy` sequences classes, initial SIDs, access vectors, default rules, optional MLS, TE/RBAC/users/constraints, indexes, initial SID contexts, fs/genfs, network, device, and Infiniband contexts. `module_policy` parses a module header followed by an avrule block, then calls `end_avrule_block()` and indexes symbols.

Class/common permission grammar maps to `define_class()`, `define_common_perms()`, and `define_av_perms()`. TE/RBAC grammar maps to type/attribute/bool/tunable definitions, AV rules, extended permissions, transitions, role rules, policy capabilities, permissive, and neveraudit actions.

Conditional grammar builds `cond_expr_t` and `avrule_t` lists, then `define_conditional()` attaches them. Constraint grammar builds postfix-style `constraint_expr_t` lists through `define_cexpr()`. Require and optional block grammar delegates to module compiler APIs.

Utility nonterminals such as `names`, `names_push`, `id_comma_list`, `mls_level_def`, `mls_range_def`, `security_context_def`, `path`, `filename`, `number`, and IP address productions control queue ordering and semantic values.

## Control Flow

The grammar is reduction-driven. Lexical rules return tokens with text in `yytext`; grammar actions call `insert_id(yytext, 0)` for normal queue order, `insert_id(..., 1)` for pushed reverse-order constraint name sets, and `insert_separator()` to delimit lists. Once a full construct is recognized, the corresponding `define_*()` function drains the queue in the expected order.

Base policies call `define_policy(pass, 0)` before class parsing. Module policies call `define_policy(pass, 1)` after `MODULE identifier version_identifier ';'`. Indexing is embedded at key points: after access-vector definitions, after TE/RBAC/users/constraints, and after module parsing.

## State and Persistence Behavior

The grammar has no persistent storage of its own beyond Bison semantic values. Its actions mutate global `id_queue`, `policydbp`, and module compiler state. Numeric semantic values are produced for ports, Xen resources, and masks; most identifiers persist only after semantic actions insert copies into policydb structures.

## Dependencies and Integration Points

It includes libsepol policy headers, `queue.h`, `module_compiler.h`, and `policy_define.h`. It depends on `policy_scan.l` for tokens and on the exact function signatures declared in `policy_define.h`. `checkpolicy` build rules generate parser C/header files from this grammar.

## Risks and Edge Cases

Queue ordering is the main fragility. Nested sets, pushed names, MLS ranges, and security contexts rely on NULL separators in precise positions. Conditional filename transitions are explicitly rejected. Extended permissions support nested ranges and omission syntax. The grammar accepts module versions as version identifiers, numbers, or IPv4-like tokens. Numeric conversions abort on `errno` and unsigned overflow.

## Test Signals

Parser tests should cover both top-level policy forms, nested name sets, constraints with all operators, conditional expressions precedence, require lists, optional/else blocks, security contexts with and without MLS ranges, IPv4/IPv6 CIDR node contexts, genfs typed and untyped forms, extended permission nested sets, and module version token variants.
