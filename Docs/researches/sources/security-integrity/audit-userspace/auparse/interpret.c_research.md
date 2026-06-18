<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/audit-userspace/auparse/interpret.c -->
# sources/security-integrity/audit-userspace/auparse/interpret.c

## Purpose
Implements auparse field interpretation: raw audit field values are converted to user-facing names, paths, flags, socket addresses, syscall argument meanings, identities, TTY data, netfilter metadata, seccomp results, and other typed strings.

## Important APIs, types, and functions
Public hidden entry points include `init_interpretation_list`, `load_interpretation_list`, `free_interpretation_list`, `interpretation_list_cnt`, `lookup_type`, `do_interpret`, UID/GID cache cleanup/metrics, `lookup_uid_from_name`, `au_unescape`, `auparse_interp_adjust_type`, and `auparse_do_interpretation`. Internals include many `print_*` converters, UID/GID lookup via `lru.c`, escaped string handling, `path_norm`, `print_sockaddr`, syscall argument dispatchers `print_a0`..`print_a3`, and generated table lookups.

## Control flow
`auparse_interpret_field` reaches `nvlist_interp_cur_val`, then `do_interpret`. `do_interpret` builds an `idata` snapshot from the current `rnode`, adjusts the field type using record type/name/value rules, then calls `auparse_do_interpretation`. That function first honors an auditd-supplied interpretation list unless it is unknown, then switches on `AUPARSE_TYPE_*` and applies escaping. Syscall argument fields branch by resolved syscall name and sometimes by other arguments, for example `setsockopt` level determines option-name table selection.

## State and persistence behavior
State is per parser except for static helper data. `au->interpretations` caches precomputed auditd interpretations, `au->uid_cache` and `au->gid_cache` cache identity lookups, and `last_type` tracks fanotify `fan_type` for the subsequent `fan_info` field. Returned interpretation strings are heap allocations cached in `nvnode.interp_val` and later freed by nvlist clearing.

## Dependencies and integration points
Depends on libaudit syscall/error/name helpers, generated tables from many `*tab.h` files, Linux network/capability/prctl/personality headers, libc password/group/protocol databases, auparse cursor helpers for contextual fields, and `nvlist`/`lru` ownership rules.

## Risks and test signals
Risks include table drift from kernel headers, argument-context mistakes, unchecked global `last_type` ordering, path normalization edge cases, conversion overflow/errno handling, buffer sizing in flag joins, identity lookup cache collisions, and cursor movement during contextual lookups such as netfilter hook family. Test signals should cover common field types, unknown fallbacks, escaped path/cwd joining, uid/gid caching and flushing, SOCKADDR decoding, syscall-argument dependent output, auditd interpretation list override, and shell/TTY escaping modes.
<!-- END_FILE_RESEARCH: sources/security-integrity/audit-userspace/auparse/interpret.c -->
