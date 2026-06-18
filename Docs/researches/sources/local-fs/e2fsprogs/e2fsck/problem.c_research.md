# File Research: sources/local-fs/e2fsprogs/e2fsck/problem.c

This file is e2fsck’s central problem registry and repair-decision engine. It maps numeric `PR_*` codes to localized descriptions, prompts, default/preen behavior, latches, fatality, logging, and follow-up actions.

Core data:
- `prompt[]` maps internal prompt IDs to user prompts such as Fix, Clear, Relocate, Connect to `/lost+found`, Clone, Delete, Optimize, and Clear flag.
- `preen_msg[]` maps prompt IDs to automatic-action text in preen mode.
- `problem_table[]` is the large ordered registry of all e2fsck problem codes from pre-pass 1 through post-pass 5.
- `pr_latch_info[]` defines grouped problem latches, including illegal blocks, bad-block inode blocks, inode/block bitmap differences, relocation hints, duplicate blocks, orphan-list refugees, oversized inodes, directory optimization, group checksum fixes, and extent optimization.

Main behavior:
- `fix_problem(ctx, code, pctx)` looks up the problem, applies one-time profile configuration overrides, prints/logs the message, asks or auto-selects an answer, updates filesystem validity and fixed-problem flags, handles fatal/preen behavior, emits problem-log XML-like entries, and executes chained `PR_AFTER_CODE` prompts.
- `end_problem_latch()` emits latch end messages and clears variable latch state.
- `set_latch_flags()` and `get_latch_flags()` manipulate latch state.
- `clear_problem_context()` zeroes a context and initializes sentinel values for `blkcount` and `group`.
- Under `UNITTEST`, `verify_problem_table()` checks ordering/duplicates.

Problem table coverage:
- Pre-pass 1: superblock, group descriptors, journal, orphan list, quota, MMP, feature compatibility, orphan-file issues.
- Pass 1: inode modes, sizes, block/extent validity, EA blocks, quota/orphan inodes, casefold/encryption, inline data, bigalloc, EA inodes.
- Pass 1B/1C/1D/1E: duplicate block rescans, directory scans for duplicate-block inodes, duplicate reconciliation, extent tree optimization.
- Pass 2: directory structure, dirents, filetypes, htree validation, checksums, encryption/casefold directory constraints, EA inode directory links.
- Pass 3/3A: directory connectivity, root and lost+found creation, parent repair, directory rehash/optimization.
- Pass 4: unattached inodes, bad refcounts, EA-inode refs, dir_nlink, spurious EA inode flags.
- Pass 5: bitmap differences, bitmap padding, summary counters, uninitialized group flags, bitmap checksums.
- Post-pass 5: journal recreation, quotas, flushing, orphan-file maintenance.

Configuration and prompting:
- Per-problem profile keys can override description, preen/no defaults, message suppression, force-no behavior, max count, and “not a fix” semantics.
- `PR_PREEN_OK` controls automatic preen repair; missing it with a prompt triggers `preenhalt()`.
- `PR_NO_OK` allows a negative answer without invalidating the filesystem.
- `PR_NOT_A_FIX` prevents accepted optimization prompts from counting as fixed corruption.
- `PR_FATAL` calls `fatal_error()` after printing.
- `PR_AFTER_CODE` chains to a second problem code.

Logging:
- Normal output goes through `print_e2fsck_message()`.
- `ctx->logf` receives human-readable problem messages and chosen answers.
- `ctx->problem_logf` receives structured `<problem .../>`, `<header .../>`, and `<suppressed .../>` records with fields copied from `problem_context`.

Risk notes:
- The problem table must remain sorted for `UNITTEST` verification even though runtime lookup is linear.
- Static problem entries are mutated after profile overrides by setting `PR_CONFIG`; this is intentional but means behavior is process-global after first use.
- Latches centralize user choice across many individual findings, so callers must end latches to clear transient state and emit closing prompts.
