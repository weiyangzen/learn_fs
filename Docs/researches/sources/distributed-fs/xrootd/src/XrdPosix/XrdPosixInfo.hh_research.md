## sources/distributed-fs/xrootd/src/XrdPosix/XrdPosixInfo.hh

Purpose: defines `XrdPosixInfo`, a small open-result carrier used when a caller needs callback, descriptor, and cache direct-file information from an open attempt.

Important APIs/types: fields `cbP`, `fileFD`, `ffReady`, `cacheURL[7]`, and `cachePath[MAXPATHLEN]`; constructor initializes callback, `fileFD=-1`, `ffReady=false`, `cacheURL` to `"file://"`, and empty cache path.

Control flow: populated by open/config code, especially `XrdPosixConfig::OpenFC()` and `XrdPosixXrootd::Open()` paths. `ffReady` plus `cachePath` can signal a direct local cache file is ready.

State and persistence: plain stack/heap data carrier; no ownership beyond callback pointer reference.

Dependencies/integration: includes platform `MAXPATHLEN` support and forward-declares `XrdPosixCallBack`.

Risks: `cacheURL[7]` stores exactly six characters plus NUL for `"file://"`; callers must not append in place beyond bounds. Callback pointer ownership is external. `cachePath` fixed length can truncate if writers are careless.

Test signals: constructor defaults; direct cache open result path; async open callback propagation; maximum path length handling.
