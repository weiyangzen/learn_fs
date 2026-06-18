# sources/test-tools/cthon04/lock/Makefile

Purpose: makefile for Connectathon file-locking tests, building native, Large File Summit, and 64-bit-lock variants from tlock.c.

Important APIs/types/functions: includes ../tests.init, defines DESTDIR and LIBS=-lm, and targets all, tlock, tlocklfs, tlock64, clean, copy, dist, lint, lint32lfs, lint64, lintall.

Control flow: all builds $(LOCKTESTS) and ensures runtests is executable. tlock compiles plain tlock.c; tlocklfs adds -DLF_SUMMIT; tlock64 adds -DLF_SUMMIT -DLARGE_LOCKS. copy/dist install binaries or sources to DESTDIR; lint targets run matching analysis modes.

State and persistence behavior: creates tlock/tlocklfs/tlock64 and object files in the lock directory; clean removes them; copy/dist write DESTDIR.

Dependencies and integration points: depends on tests.init for CC, CFLAGS, and LOCKTESTS selection. The produced programs integrate with lock/runtests.

Risks: recursive `make $(LOCKTESTS)` inherits environment-sensitive target names; DESTDIR defaults invalid; all variants share one source so macro-specific behavior must be tested separately.

Test signals: successful build of configured LOCKTESTS and executable runtests; lint targets provide static-analysis signals for each offset/locking mode.
