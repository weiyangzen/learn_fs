# sources/test-tools/cthon04/general/large.c

Purpose: historical C compiler-driver source used as a large-ish compile workload for the general tests, not as a maintained compiler frontend.

Important APIs/types/functions: global tool paths cpp/ccom/c2/as/ld/crt0; argument lists av/clist/llist/plist; flags for -S, -o, -R, -O, -p, -g/-go, -w, -E/-P, -c, -D/-I/-U/-C, -t, -B, -d. Functions include main(), idexit(), dexit(), error(), getsuf(), setsuf(), callsys(), nodup(), savestr(), and strspl().

Control flow: parses compiler-style arguments into preprocessing, compile, assemble, and link lists; optionally rewrites pass paths; creates /tmp/ctm<pid> temporary names; runs cpp, ccom, optional c2, as, and ld via fork/exec/wait; cleans temporaries on normal exit or signal.

State and persistence behavior: writes temporary files under /tmp, writes .o/.s/.i outputs according to flags, may link an executable, and removes selected temporary/object files depending on compile/link mode.

Dependencies and integration points: depends on old Unix compiler pass paths and libc calls. The general Makefile copies this source to large1.c-large3.c so large4.sh can compile four similar files in parallel.

Risks: old K&R C with implicit declarations; fixed temporary-name buffers; no robust wait error handling; hard-coded tool paths rarely exist on modern systems; primarily useful as test input.

Test signals: in this suite, the signal is successful compilation/removal by make or large4.sh rather than correctness of the compiler driver itself.
