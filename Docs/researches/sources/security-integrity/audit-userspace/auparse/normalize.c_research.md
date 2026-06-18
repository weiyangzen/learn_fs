<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/audit-userspace/auparse/normalize.c -->
# sources/security-integrity/audit-userspace/auparse/normalize.c

## Purpose
Implements auparse event normalization: it analyzes the current audit event and identifies event kind, session, subject, action, object, results, execution method, key, and subject/object attributes through stable getter APIs.

## Important APIs, types, and functions
Lifecycle helpers are `init_normalizer` and `clear_normalizer`. Main entry point is `auparse_normalize`. Getter APIs include `auparse_normalize_get_event_kind`, session/subject/object/result/key cursor seekers, attribute iterators, subject/object kind getters, action, and how. Internals include field-coordinate encoding macros, `normalize_simple`, `normalize_compound`, `normalize_syscall`, object/subject setters, file/socket/program object collectors, event-kind classification, and simple-object finders.

## Control flow
`auparse_normalize` resets state and chooses compound normalization for multi-record events or simple normalization for single-record events. Compound events locate a syscall record, interpret syscall name and success, collect subject/session/how/key, and delegate action/object inference to syscall or record maps. Simple events use record-type-specific branches for config, login, daemon, AVC, BPF, listener, MAC, user, crypto, virt, TTY, and anomaly events. Getters later call `seek_field` to reposition the parser cursor to stored record/field coordinates.

## State and persistence behavior
Normalized state is held in `au->norm_data`. Field references are encoded as 32-bit record/field coordinates with `UNSET` sentinels; strings like action/how/subject-kind are heap-owned; attribute coordinates live in `cllist`. `syscall_success` is file-static and reset with the normalizer.

## Dependencies and integration points
Depends on libaudit record constants, auparse cursor and interpretation APIs, UID lookup, `normalize-llist`, generated normalization maps, and Linux file-mode macros. It is the semantic bridge between raw auparse records and higher-level reporting APIs.

## Risks and test signals
Risks include cursor side effects, hard-coded record ordering for PATH/CWD/SOCKADDR records, global `syscall_success`, incomplete syscall/record maps, interpreter command special casing, and object-kind ambiguity for AVC/MAC/security events. Tests should cover simple and compound events, failed syscalls, path parent fallback, rename/mount/link record ordering, attribute iteration, no-attribute mode, cursor reset after normalization, and every getter return state.
<!-- END_FILE_RESEARCH: sources/security-integrity/audit-userspace/auparse/normalize.c -->
