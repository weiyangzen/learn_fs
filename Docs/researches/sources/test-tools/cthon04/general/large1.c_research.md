# sources/test-tools/cthon04/general/large1.c

Purpose: generated copy of general/large.c used to create an additional independent compile workload.

Important APIs/types/functions: byte-for-byte identical to large.c in this checkout, so it contains the same compiler-driver globals and functions: main(), idexit(), dexit(), error(), getsuf(), setsuf(), callsys(), nodup(), savestr(), and strspl().

Control flow: same as large.c: parse cc-like flags, run cpp/ccom/c2/as/ld passes, and clean temporary files.

State and persistence behavior: same temporary and output behavior as large.c. Its existence is itself generated state from the general Makefile.

Dependencies and integration points: created by `cp large.c large1.c`; compiled by large4.sh in parallel with large.c/large2.c/large3.c.

Risks: should not be edited independently because regeneration overwrites it; all large.c portability/security limitations apply.

Test signals: successful generation and compilation are the relevant harness signals.
