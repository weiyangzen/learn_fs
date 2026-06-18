# sources/user-network-fs/nfs-ganesha/src/scripts/checkpatch.pl

## Purpose
This is a Perl style and patch-quality checker derived from Linux `checkpatch.pl` version 0.32. In this NFS-Ganesha tree it validates patches or full source files against kernel-oriented coding conventions. It can read unified diffs from files or stdin, synthesize diffs for `--file` checks, expand `--git` revision expressions into `git format-patch` streams, filter message types, emit colorized reports, and optionally write experimental mechanical fixes.

## Important APIs, Types, And Functions
The script is an executable CLI, not a reusable Perl module. Its public interface is the option set parsed by `GetOptions`: patch/file/git modes, strict checks, message filtering, line length, tree root, fix modes, spelling/codespell, typedef injection, and color/report formatting.

The central entry points are `process($filename)` and the message helpers `ERROR`, `WARN`, and `CHK`, which funnel through `report`. Parsing helpers include `sanitise_line`, `ctx_statement_block`, `ctx_statement_full`, `ctx_block_get`, `annotate_values`, `build_types`, `possible`, `parse_email`, `format_email`, `seed_camelcase_file`, and `git_commit_info`. Regex fragments such as `$Ident`, `$Type`, `$Declare`, `$Lval`, `$FuncArg`, and `$balanced_parens` form the effective parser.

## Control Flow
Startup reads optional `.checkpatch.conf`, parses CLI options, validates incompatible modes, configures colors, loads verbose docs/spelling/typedef data, and verifies a Linux-kernel-like root unless disabled. Inputs are opened directly, converted from files with `diff -u /dev/null`, or generated from commits with `git format-patch`.

`process` first sanitizes raw diff lines, tracks hunk and comment state, and then performs a line-oriented rules pass. It updates real file/line context from diff headers, validates commit metadata/signoffs, counts changed lines, gathers multi-line C statement context, and runs many anchored checks. At completion it prints accumulated reports and summaries and may write fixed output for `--fix` or `--fix-inplace`.

## State And Persistence
Runtime state is mostly global: CLI flags, filters, type regexes, raw/sanitized/fixed line arrays, fix insertion/deletion queues, counters, and spelling/type caches. Persistent side effects include `.checkpatch-camelcase.*` caches, optional experimental fix files, or in-place rewrites. It reads `.checkpatch.conf`, `spelling.txt`, optional codespell and typedef files, `const_structs.checkpatch`, and optional docs.

## Dependencies And Integration Points
Perl dependencies are `POSIX`, `File::Basename`, `Cwd`, `Term::ANSIColor`, `Encode`, and `Getopt::Long`. External tools include `git`, `diff`, `find`, `grep`, `python`, `python3`, `codespell`, `scripts/spdxcheck.py`, and `scripts/get_maintainer.pl` when available. Full tree-aware operation expects a Linux kernel source layout, which is a mismatch for plain NFS-Ganesha use unless `--no-tree` or a compatible root is supplied.

## Risks And Edge Cases
The checker is heuristic and regex-heavy, so complex macros, generated code, non-kernel style, and unusual declarations can produce false positives or missed defects. Some command invocations interpolate paths/revisions. Dynamic type learning can affect later checks in the same file. `--fix` is explicitly experimental and can produce invalid rewrites when context is misclassified.

## Test Signals
Run `perl -c`, `--list-types`, representative bad/clean patch checks, `--file --no-tree` checks, and comparisons against upstream Linux checkpatch behavior. In this repository, include tests proving non-kernel-tree invocation works through `--no-tree`.
