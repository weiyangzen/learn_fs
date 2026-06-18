## sources/distributed-fs/xrootd/src/XrdSys/XrdSysE2T.cc

Purpose: implements thread-safe errno-to-text conversion with cached strings and platform adjustments.

Important APIs/types/functions: `XrdSysE2T(int errcode)` returns a stable `const char *`; local `initErrTable()` precomputes known error strings into `Errno2String`; `e2sMap` stores generic messages for unknown positive error codes; `e2sMutex` guards the map.

Control flow: static initialization preloads slots 1..143 using `strerror(ERRNOBASE+i)`, lowercases the first character, remaps `EBADE` to an authentication-focused message, fills holes up to the last known error, and sets slot 0 to "no error". Calls return immediately for 0 and known ranges, return "negative error" for negative values, or lazily create `"unknown error N"` in the map.

State and persistence: process-lifetime allocated strings and map entries; no deallocation is attempted. This is intentional stable-storage behavior for returned pointers.

Dependencies and integration: uses C library `strerror`, `strdup`, `tolower`, STL `map`/`string`, and `XrdSysMutex`. Used by logging, plugin loading, IOEvents, and error reporting.

Risks: returning `eTxt.c_str()` after unlocking is safe only because `std::map` node storage is stable for non-erased entries; heavy insertion from many unknown codes still grows memory. Static initialization depends on pthread mutex readiness.

Test signals: known errno, unknown positive code, negative code, GNU/Hurd `ERRNOBASE`, `EBADE` remapping, and concurrent lookup of unknown codes.
