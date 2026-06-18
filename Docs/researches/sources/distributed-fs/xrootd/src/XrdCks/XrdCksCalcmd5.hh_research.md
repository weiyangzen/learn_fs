# sources/distributed-fs/xrootd/src/XrdCks/XrdCksCalcmd5.hh

Purpose: declares the MD5 `XrdCksCalc` subclass and its internal context.

Important APIs and types: public methods are `Current`, `Init`, `New`, `Final`, `Update`, and `Type`. `Type()` returns `"md5"` and a 16-byte size. Private `MD5Context` stores four state words, bit counters, and a 64-byte input block through unions; helper methods are `byteReverse`, `MD5Update`, and `MD5Transform`.

Control flow and integration: managers stream file data through `Update()`, then call `Final()` or `Current()`. `New()` supports calculator cloning.

State and persistence: mutable MD5 context and digest buffer are per instance. Final digest bytes may be serialized in `XrdCksData`.

Dependencies: includes `XrdCksCalc.hh` and `<cstdio>`.

Risks and test signals: tests should verify `Current()` preserves state, `Type()` reports correct length, and incremental hashing matches known MD5 vectors.
