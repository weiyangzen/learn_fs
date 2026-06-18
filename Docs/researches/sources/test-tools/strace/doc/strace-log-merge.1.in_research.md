# sources/test-tools/strace/doc/strace-log-merge.1.in

## Purpose
Provides the generated manpage template for `strace-log-merge`, documenting the helper that merges `strace -ff -tt[t]` per-process logs by prepending PIDs and sorting lines chronologically.

## Important APIs, Types, and Functions
Read coverage: 131 lines and 3409 bytes. The roff template defines an `.OR` macro for required options, a `.TH` header using `@SLM_MANPAGE_DATE@` and `@VERSION@`, and sections for NAME, SYNOPSIS, DESCRIPTION, OPTIONS, EXIT STATUS, USAGE EXAMPLE, NOTES, BUGS, HISTORY, REPORTING BUGS, and SEE ALSO. User-facing interface items are `strace-log-merge STRACE_LOG` and `strace-log-merge --help`. The documented input pattern is `STRACE_LOG.*`.

## Control Flow
There is no executable logic, but the documentation describes operational flow: run strace with `-o prefix -ff -tt` or `-ttt`, invoke `strace-log-merge prefix`, read all matching per-PID files, prepend PID to each line, and sort combined output by timestamp. The usage example traces several sleeps, folds output, and shows merged `execve`, `nanosleep`, exit, and `SIGCHLD` lines.

## State and Persistence Behavior
The template is transformed by configure into `doc/strace-log-merge.1` with the current manpage date and package version. The utility documented by the manpage reads log files but does not persist merged output unless the caller redirects it. Documentation notes that input files are assumed to be correctly formatted logs from one strace session.

## Dependencies and Integration Points
Depends on roff/man macro processing and Autoconf substitution from `configure.ac`. It integrates with the `src/strace-log-merge` utility, `doc/strace.1`, packaging manpage installation, strace's `-ff`, `-tt`, and `-ttt` options, and bug-reporting via the strace mailing list.

## Risks and Edge Cases
The NOTES section documents a key sorting risk: `-tt` timestamps lack dates, so logs spanning midnight may sort incorrectly; `-ttt` avoids that by including date-capable timestamps. The BUGS section states the utility does not validate input format and assumes all `STRACE_LOG.*` files belong to one correctly formatted session. Glob overmatch, mixed sessions, malformed logs, locale-sensitive sorting, or timestamps without enough precision are practical edge cases.

## Test Signals
Validate `configure` substitutes date and version, `man`/`mandoc` can parse the generated page, `strace-log-merge --help` matches documented synopsis, examples work against actual `strace -ff -tt` logs, `-ttt` logs sort across midnight or date boundaries, and malformed or mixed-prefix inputs produce documented non-zero/error behavior where applicable.
