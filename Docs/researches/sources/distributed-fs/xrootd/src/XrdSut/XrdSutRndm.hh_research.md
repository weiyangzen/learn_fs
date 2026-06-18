## sources/distributed-fs/xrootd/src/XrdSut/XrdSutRndm.hh

Purpose: declares `XrdSutRndm`, the security utility random-bit provider used by SUT code to produce random buffers, random strings, unsigned integers, and random tags.

Important APIs/types/functions: `static bool fgInit` tracks one-time initialization; the constructor lazily invokes `Init()`; `Init(bool force=false)` initializes or reinitializes the provider; `GetBuffer(int len, int opt=-1)` returns a newly supplied random byte buffer; `GetString(int opt, int len, XrdOucString&)` and `GetString(const char *copt, int len, XrdOucString&)` fill an `XrdOucString`; `GetUInt()` returns a random unsigned integer; `GetRndmTag()` fills a random tag.

Control flow: this header only declares the interface, but its constructor contract makes object creation a lazy initializer. Callers then use static methods directly.

State and persistence: state is process-local static state only. No persistent storage is declared here. Returned buffers likely transfer ownership to callers, so implementation and callers must agree on allocation/freeing.

Dependencies and integration: includes `XrdSutAux.hh` and forward-declares `XrdOucString`. It is consumed by SUT authentication/security helpers needing entropy.

Risks: weak initialization, non-thread-safe `fgInit` updates, ambiguous buffer ownership, and option parsing differences between integer and string options are the main risks.

Test signals: tests should cover lazy initialization, forced reinitialization, buffer length and null handling, string option variants, uniqueness/distribution smoke checks, and concurrent initialization calls.
