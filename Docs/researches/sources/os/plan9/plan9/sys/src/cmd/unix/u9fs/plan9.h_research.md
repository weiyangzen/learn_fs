# File Research: sources/os/plan9/plan9/sys/src/cmd/unix/u9fs/plan9.h

- Role: Portability shim that gives Unix builds Plan 9-like types, constants, argument parsing macros, UTF declarations, formatting declarations, Qid/Dir definitions, and DES prototypes.
- Key content: Large-file feature macros, platform workarounds for SGI/Sun, `uchar`/`ulong`/`vlong` aliases, `ARGBEGIN`, open mode constants, Qid type bits, Dir mode bits, `Qid`, and `Dir`.
- Integration: Included first by most u9fs support files to normalize the Unix C environment.
- Risks/notes: Sets `UTFmax` to 3 while `rune.c` has code paths for 4-byte UTF guarded by `UTFmax >= 4`; this preserves older Plan 9 UTF behavior.
