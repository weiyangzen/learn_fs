
<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/rsync/popt/popt.c -->
# Research: sources/sync-backup/rsync/popt/popt.c

## Purpose
`popt/popt.c` is the core implementation of the bundled popt option parser used by rsync. It creates parser contexts, walks argv/options/aliases, saves typed option arguments, supports callbacks, leftovers, alias expansion, exec actions, argument stripping, and bitset helper operations.

## Important APIs, Types, and Functions
- Context lifecycle: `poptGetContext()`, `poptResetContext()`, and `poptFreeContext()`.
- Callback dispatch: `invokeCallbacksPRE()`, `invokeCallbacksPOST()`, and `invokeCallbacksOPTION()`.
- Option and alias machinery: `findOption()`, `longOptionStrcmp()`, `handleAlias()`, `handleExec()`, `poptAddAlias()`, `poptAddItem()`, `poptStuffArgs()`.
- Argument parsing and saving: `poptGetNextOpt()`, `poptGetOptArg()`, `poptGetArg()`, `poptPeekArg()`, `poptGetArgs()`, `poptSaveArg()`, `poptParseInteger()`, `poptSaveLongLong()`, `poptSaveLong()`, `poptSaveInt()`, `poptSaveShort()`, `poptSaveString()`, `poptSaveBits()`.
- Bitset helpers: `poptBitsAdd()`, `poptBitsChk()`, `poptBitsClr()`, `poptBitsDel()`, `poptBitsIntersect()`, `poptBitsUnion()`, `poptBitsArgs()`.
- Error/report helpers: `poptBadOption()`, `poptStrerror()`, `poptGetInvocationName()`, `poptStrippedArgv()`, `poptSetExecPath()`.

## Control Flow
`poptGetContext()` allocates and initializes a context, sets the initial option stack entry, applies POSIX environment flags, stores the application name, and invokes pre-parse callbacks. `poptGetNextOpt()` is the central loop: it pops exhausted alias/stuffed stack entries, handles end-of-input post callbacks/maincall/exec, classifies leftovers and `--`, parses long options including `--opt=arg`, tries aliases and exec triggers, falls back to short-option clusters, finds option descriptors, consumes required/optional arguments, expands `!#:+` substitutions, saves typed values, invokes callbacks, records final argv, and returns option values.

Alias expansion pushes a new option-stack entry with duplicated argv. Exec handling records a target command and later `execCommand()` builds argv from exec args, final option argv, and leftovers, drops elevated privileges where possible, and calls `execvp()`. Context reset/free paths release leftovers, aliases, execs, stacked argv, final argv, help strings, exec path, and bitmaps.

## State and Persistence
All parser state lives in `poptContext`: option stack, argv indexes, `nextCharArg`, `nextArg`, leftovers, aliases, exec definitions, final argv, strip bitmap, flags, callbacks, and exec failure. Module globals `_poptArgMask`, `_poptGroupMask`, and bitset sizing parameters tune parser masks and bitset behavior. No durable state is written; `execCommand()` replaces the process image on success.

## Dependencies and Integration Points
It depends on popt internal headers/macros, allocation helpers, bitmap macros, string helpers, `poptJlu32lpair()` from lookup3 for bitsets, libc parsing (`strtoll`, `strtod`), process APIs (`execvp`, uid/gid drops), and environment variables `POSIXLY_CORRECT`/`POSIX_ME_HARDER`. Rsync integrates through `options.c` by creating contexts, reading defaults, adding unaliases, fetching options, and reporting errors.

## Risks
This is security-sensitive parser code. Alias stack depth, argument ownership, optional-argument rules, final argv growth, and exec privilege dropping are key correctness points. Some comments mark memory leaks as application-owned for saved strings/argv/bitsets. String-command exec path handling and alias substitution must avoid unexpected argument injection. Numeric parsing currently lacks suffix support and treats extrema as overflow sentinels. Alignment checks in typed saves can reject unusual pointers. Bloom-style bitset deletion can create false negatives by clearing shared bits.

## Test Signals
Parser tests should cover long/short options, short clusters, `--opt=arg`, split args, optional args, unwanted args, `--`, POSIX leftover mode, aliases with depth limits and argument substitution, callbacks, typed saves and overflow, toggle/no- prefix behavior, strip argv, exec registration with privilege dropping, stuffed args, bad-option reporting, and bitset add/check/delete/intersection/union behavior.
<!-- END_FILE_RESEARCH: sources/sync-backup/rsync/popt/popt.c -->
