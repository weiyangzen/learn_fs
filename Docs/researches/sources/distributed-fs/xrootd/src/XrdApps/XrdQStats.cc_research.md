# sources/distributed-fs/xrootd/src/XrdApps/XrdQStats.cc

Purpose: implements `xrdqstats`, a client-side stats query utility that asks an XRootD server for selected statistic categories and prints XML or converted text/flat/CGI output.

Important APIs/types/functions: `Fatal` reports failed `XRootDStatus`; `Usage` documents options; `main` parses `-f`, `-i`, `-n`, `-s`, `-z`, constructs an `XrdCl::URL`, creates a `FileSystem`, performs `Query(QueryCode::Stats, ...)`, and formats with `XrdMpxXml`.

Control flow: statistics letters default to `bldpsu`; `c` is normalized to `l`. Count/interval rules make one-shot default, repeated default every 10 seconds when `-n` is given, and endless looping when only `-i` is given. Each loop queries the server, writes raw XML for `fmtXML`, or converts through `XrdMpxXml::Format` and writes with EINTR retry.

State and persistence: maintains only local loop counters and buffers. No persistence; repeated operation depends entirely on remote server stats.

Dependencies and integration points: uses XrdCl URL/FileSystem/Buffer/XRootDResponses and shares formatter code with `mpxstats`.

Risks: the write loop has the same non-EINTR write error handling gap as `mpxstats`. `obuff` is fixed at 65536 with no bounds contract from `Format`. `-d` is accepted but not listed in usage options except via `valOpts`; debug only affects formatter behavior.

Test signals: all format modes, zero suppression in text mode, stats letter validation, count/interval matrix, invalid URL handling, xrootd error response extraction, and repeated query behavior.
