# sources/security-integrity/selinux/checkpolicy/parse_util.c

## Purpose

`parse_util.c` provides `read_source_policy()`, a shared helper for checkpolicy/checkmodule-style tools to parse a textual SELinux policy source into an already initialized `policydb_t`. It centralizes file opening, parser global setup, two-pass parsing, cleanup of parser resources, and user-facing error reporting.

## Important APIs and Functions

`read_source_policy(policydb_t *p, const char *file, const char *progname)` opens `file` as `yyin`, creates the global `id_queue`, sets `mlspol` from `p->mls`, assigns global `policydbp`, initializes `policydbp->name`, and runs the yacc parser twice. It calls `init_parser(1, file)`, `yyparse()`, rewinds the file, calls `init_parser(2, file)`, `yyrestart(yyin)`, and parses again. It treats either a nonzero parser return or nonzero `policydb_errors` as failure.

## Control Flow

The helper is linear and cleanup-oriented. It returns immediately if the source file cannot be opened. Once `id_queue` exists, all failures go through `cleanup`, which destroys the queue, closes `yyin`, and calls `yylex_destroy()`. A successful two-pass parse sets `rc = 0`.

## State and Persistence Behavior

The function mutates global parser variables declared in `policy_define.c` and `policy_scan.l`: `yyin`, `id_queue`, `policydb_errors`, `policydbp`, and `mlspol`. It also writes `policydbp->name = strdup(file)`. The parsed policy contents persist in the caller-provided `policydb_t`; parser temporaries are destroyed before returning.

## Dependencies and Integration Points

This file depends on `parse_util.h`, `queue.h`, generated yacc/flex symbols, and libsepol `policydb_t`. It is used wherever a source policy needs to be read without immediately running higher-level assertion or hierarchy checks. It assumes the caller already created and configured the policydb, including policy type and target settings.

## Risks and Edge Cases

The helper has process-global parser state and is not reentrant. It overwrites `policydbp->name` without freeing any existing name at this layer, so callers should pass a fresh or appropriately managed policydb. If pass 1 partially mutates `policydb_t` and pass 2 fails, the caller receives `-1` with partial state still in `p`. Cleanup always destroys `id_queue`; other globals are left pointing at closed/destroyed resources until the next parse setup.

## Test Signals

Tests should cover unreadable files, allocation failure paths where practical, pass-1 syntax errors, pass-2 semantic errors, MLS and non-MLS policydb setup, and repeated calls in one process to detect stale flex/parser state.
