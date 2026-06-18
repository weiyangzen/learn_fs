# sources/distributed-fs/xrootd/src/XrdCks/XrdCksWrapper.hh

Purpose: declares a forwarding wrapper base for stacked checksum plugins. A plugin can derive from `XrdCksWrapper`, override selected `XrdCks` methods, and delegate everything else to the previous checksum plugin in the chain.

Important APIs: forwarding implementations for `Calc` with and without callback, `Del`, `Get`, `Config`, `Init`, `List`, `Name`, `Object`, `Size`, `Set`, and `Ver`. The protected `cksPI` reference is the antecedent plugin. The file also documents the `extern "C" XrdCksAdd2` factory signature via `XRDCKSADD2PARMS`.

Control flow/state: no persistence or independent algorithm state exists here; state is whatever the wrapped plugin owns. Dependencies include `XrdCks`, `XrdCksData`, `XrdCksCalc`, `XrdOucEnv`, and `XrdSysError`. Integration point is the stacked-plugin loader resolving `XrdCksAdd2`. Risks: lifetime of the previous plugin reference, callback overloads silently ignoring callbacks by default, and plugins forgetting to declare version metadata. Test signals: pass-through behavior, selective override behavior, stacked factory loading, and callback overload expectations.
