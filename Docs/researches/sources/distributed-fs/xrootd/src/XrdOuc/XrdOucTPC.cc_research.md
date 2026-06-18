# sources/distributed-fs/xrootd/src/XrdOuc/XrdOucTPC.cc

Purpose: implements third-party-copy CGI helpers that generate and filter `tpc.*` query fragments for source and destination negotiation.

Important APIs, types, and functions: static key names define all supported `tpc.*` parameters. `cgiC2Dst()` builds destination-side CGI with key, source, logical file name, checksum, stream count, delegation host, source/target protocols, push, and delegation-on flag. `cgiC2Src()` builds source-side CGI with key, destination host, and optional TTL. `cgiD2Src()` forwards origin information. `cgiHost()` parses optional user and port, resolves host canonical name through `XrdNetAddr`, and `copyCGI()` copies user CGI keys while filtering system prefixes.

Control flow: CGI builders validate required parameters and buffer length, normalize host specs through `cgiHost()`, then append parameters with `snprintf()` while tracking remaining buffer space. `copyCGI()` skips leading ampersands, treats tab as the input separator, requires an equals sign, filters `tpc.`, `xrd.`, and `xrdcl.` prefixes, and emits ampersand-separated output.

State and persistence: only static constant key strings are global. Per-call state is stack/heap memory owned by `tpcInfo`, which frees a duplicated hostname. No persistence or locking exists.

Dependencies and integration points: depends on `XrdNetAddr` for hostname normalization and is consumed by XRootD TPC flows that pass CGI strings between clients, sources, destinations, and delegates.

Risks and test signals: the final overflow test compares only the last `snprintf()` result with remaining length, so earlier truncation can be hard to distinguish. Inputs are inserted without URL encoding. `cgiHost()` resolution can block or fail depending on DNS. Tests should cover IPv6 bracket parsing, user@host:port, buffer truncation, optional parameter combinations, filtering in `copyCGI()`, and canonical host failures.
