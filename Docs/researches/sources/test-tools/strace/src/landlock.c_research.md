# sources/test-tools/strace/src/landlock.c

Purpose: decodes Landlock ruleset creation, rule addition, and self-restriction syscalls.

Important APIs/types/functions: `SYS_FUNC(landlock_create_ruleset)`, `SYS_FUNC(landlock_add_rule)`, `SYS_FUNC(landlock_restrict_self)`, `print_landlock_ruleset_attr`, `print_landlock_path_beneath_attr`, `print_landlock_net_port_attr`, and xlats for create flags, rule types, filesystem access, network access, and scope flags.

Control flow: ruleset creation decodes only fields present in the supplied size, from mandatory filesystem access through newer network and scope fields, and returns fd status unless version/errata flags mean no fd. `landlock_add_rule` prints the ruleset fd, dispatches the rule attribute by rule type, then prints raw flags. Restrict self prints fd and raw flags.

State and persistence behavior: no persistent state. Reads tracee memory for ruleset and rule attribute structures with size-aware bounds.

Dependencies and integration points: depends on `<linux/landlock.h>`, fd printers, and generated Landlock xlat tables. Integrated as syscall decoders for Landlock's dedicated syscalls.

Risks: Landlock structures are extensible; size checks must avoid reading beyond known fields while showing trailing data. New rule types currently fall back to raw addresses.

Test signals: cover minimal and extended ruleset sizes, version/errata no-fd return behavior, filesystem and network rule attributes, unknown rule type fallback, scope flags, and inaccessible attribute pointers.
