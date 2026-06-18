# sources/test-tools/ltp/testcases/kernel/fs/doio/include/databin.h

Purpose: `databin.h` declares binary pattern generation and validation helpers for growfiles stress modes that are not simple ASCII or pid/offset word formats. These modes give the filesystem tests compact ways to fill buffers with deterministic bit patterns.

Important APIs and types: `databingen(int mode, char *buffer, int bsize, int offset)` fills a buffer. `databinchk(int mode, char *buffer, int bsize, int offset, char **errmsg)` validates a buffer and reports mismatch details. Documented modes are `'a'` alternating bits, `'c'` checkerboard, `'C'` counting, `'o'` all ones, `'z'` zeros, and `'r'` random integers.

Control flow: this header has declarations only. The comments state that every mode except random is file-offset based, allowing multiple writers to generate compatible content for the same byte ranges.

State and persistence behavior: deterministic modes persist in file data and can be verified later from mode plus offset. Random mode is explicitly not checkable by the same deterministic mechanism and causes `growfiles.c` to disable file checking.

Dependencies and integration points: `growfiles.c` calls `databingen()` for binary patterns in `growfile()` and `databinchk()` in both last-write and whole-file checks. It is part of the pattern abstraction beside `dataascii` and datapid helpers.

Risks: `mode` is an untyped integer/character with no enum, so invalid modes are possible. The API does not document return values for generation and only loosely documents checker error semantics. Offset/count width is `int`.

Test signals: tests should cover each deterministic mode at nonzero offsets, corruption reporting, random generation being excluded from validation, and boundary sizes that are not aligned to the implementation's natural word size.
