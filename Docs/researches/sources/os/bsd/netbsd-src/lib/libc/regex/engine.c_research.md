# File Research: sources/os/bsd/netbsd-src/lib/libc/regex/engine.c

Core regex execution engine included multiple times by `regexec.c` with different state-set and character conversion macros. It implements matching over the compiled strip representation from `regex2.h`.

Major functions:
- `matcher()` sets up bounds, optional `REG_STARTEND`, Boyer-Moore “must” prescreening, and submatch/backreference handling.
- `walk()` runs the NFA state propagation across the subject and tracks possible match endpoints.
- `step()` transitions state sets through strip operators.
- `dissect()` reconstructs submatch boundaries for regexes without backreferences.
- `backref()` recursively validates matches requiring backreference equality and captures.
- `stepback()` helps adjust start positions for must-string offsets, including multibyte-aware stepping under NLS.

The engine supports anchors, BOS/EOS, word boundaries, non-word boundaries, bracket sets, alternation, plus/question loops, and backreferences. Backreferences use recursion with `MAX_RECURSION` guard for empty references. Debug printing is compiled only under `REDEBUG`.
