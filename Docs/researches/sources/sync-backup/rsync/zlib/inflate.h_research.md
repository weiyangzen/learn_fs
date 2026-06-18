# sources/sync-backup/rsync/zlib/inflate.h

Purpose: private header defining the inflate state machine and persistent decompressor state. It is internal to zlib and should not be consumed by applications.

Important APIs/types/functions: defines `GUNZIP` unless `NO_GZIP` is set, undefines conflicting `BAD` on AIX, declares the `inflate_mode` enum, and defines `struct inflate_state`. Modes include wrapper/header states, block states, decode states, trailer states, and terminal/error states. `struct inflate_state` holds mode flags, wrapper selection, checksum totals, gzip header pointer, circular window, bit accumulator, copy/decode variables, dynamic table arrays, `codes[ENOUGH]`, invalid-distance policy, and `inflateMark` tracking fields.

Control flow: the enum documents the intended transitions: header parsing to `TYPE`, stored/dynamic/fixed block handling to code decode states, literal/match loops back to `LEN`, and trailer validation to `DONE`. `inflate.c` implements the transitions directly in a switch and relies on enum ordering in a few comparisons such as update-window decisions before `BAD`.

State and persistence: this header is the canonical layout of decompressor state preserved between `inflate()` calls. It enables partial input/output operation by saving every variable needed to resume: current mode, bit buffer, pending length/distance, table-building progress, window history, and gzip header-copy progress.

Dependencies and integration points: requires `code` and `ENOUGH` from `inftrees.h`, public `gz_headerp` and zlib types, and `FAR` portability macros. It is included by `inflate.c` and `inffast.c`; the fast path reads fields directly, so layout and semantics are cross-file contracts.

Risks: adding modes or reordering terminal states can change comparisons in `inflate.c`. Changing array sizes (`lens`, `work`, `codes`) without corresponding table-builder changes can cause memory corruption. `sane` and invalid-distance compatibility are security-relevant because they decide whether malformed streams error or synthesize zero output.

Test signals: compile and run all inflate modes with gzip enabled/disabled, test partial-buffer resumption for every major state, and run malformed-stream fuzzers that interrupt during header, table, match, and trailer phases.
