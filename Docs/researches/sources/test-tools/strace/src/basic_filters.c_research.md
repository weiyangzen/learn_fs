# sources/test-tools/strace/src/basic_filters.c

Purpose: implements parsing of basic syscall and numeric qualification filters used by `-e trace=...` and similar options.

Important APIs/types/functions: `personality_designators`, `qualify_syscall_separate_personality`, `qualify_syscall_number`, `qualify_syscall_regex`, `qualify_syscall_class`, `scno_by_name`, `qualify_syscall_name`, `qualify_syscall_pers`, `qualify_syscall`, `qualify_syscall_tokens`, and generic `qualify_tokens`.

Control flow: filter strings are cleared/inverted according to leading `!`, handle `none`/`all`, split comma-separated tokens, and resolve each token as number, regex, class, or syscall name across all personalities or a suffix-specific personality such as `@64`. Numeric syscalls are shuffled/validated per personality before adding to number sets.

State and persistence behavior: mutates caller-provided `number_set` arrays. It reads global syscall tables `sysent_vec`/`nsyscall_vec` and architecture personality metadata.

Dependencies and integration points: supports CLI filtering documented in `strace.1.in`; uses regex library, number-set helpers, syscall table vectors, xlat lookup, and error handling.

Risks: invalid filters terminate with help/error messages. Regex matching traverses all syscall names and can be costly but bounded by syscall table sizes. Personality suffix parsing treats unknown suffixes as fatal.

Test signals: option parsing tests for names, numbers, regexes, classes, negation, `none`, `all`, `?` suppression, and `@` personality suffixes should exercise this file.
