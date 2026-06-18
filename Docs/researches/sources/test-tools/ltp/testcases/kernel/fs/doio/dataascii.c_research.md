# sources/test-tools/ltp/testcases/kernel/fs/doio/dataascii.c

Purpose: generates and verifies repeating ASCII data patterns for doio read/write validation.

Important APIs/types/functions: `dataasciigen`, `dataasciichk`, default `CHARS`, `Errmsg`, optional `UNIT_TEST` main, `strlen`, and `sprintf`.

Control flow: generation selects either caller-provided character list or default alphabet/newline pattern, then fills `buffer` from `offset` through `offset + bsize` by indexing `cnt % chars_size`. Checking mirrors the same sequence and returns the file offset of the first mismatch, setting `*errmsg` to static `Errmsg`; on success it returns `-1` and reports all bytes matched.

State/persistence behavior: writes caller-provided memory only and uses one static error buffer, making it non-reentrant/thread-unsafe for concurrent checks.

Dependencies/integration: used by doio data fill/check plumbing via `dataascii.h`. Optional unit test allocates memory and exercises aligned/shifted/mismatch cases.

Risks/test signals: empty custom `listofchars` would cause modulo by zero. Static error storage can be overwritten by subsequent calls. Success signal is return `-1`; nonnegative return is the failing absolute offset.
