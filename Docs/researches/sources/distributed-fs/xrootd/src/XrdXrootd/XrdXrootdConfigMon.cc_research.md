# sources/distributed-fs/xrootd/src/XrdXrootd/XrdXrootdConfigMon.cc

Purpose: implements monitor and generic stream configuration for the xrootd protocol. It parses `monitor` and `mongstream` directives, stores defaults in a temporary parameter object, constructs g-stream providers, configures TPC monitoring, and initializes `XrdXrootdMonitor`.

Important APIs and functions: `ConfigMon()` applies `MonParms` defaults to `XrdXrootdMonitor`, initializes phase-one monitoring, calls `ConfigGStream()`, then enables monitoring. `ConfigGStream()` creates `XrdXrootdGSReal` objects for enabled provider streams (`ccm`, `oss`, `http`, `pfc`, `TcpMon`, `Throttle`, `Tpc`) and publishes them into the xrootd or outer environment. `xmon()` parses event monitoring options including flush intervals, file-stat options (`lfn`, `ops`, `ssq`, `xfr`), buffer sizes, ident records, redirection stream counts, timing window, and up to two UDP destinations. `xmondest()` validates and canonicalizes host:port endpoints. `xmongs()` selects g-streams and applies `flush`, `maxlen`, and `send` options. `xmongsend()` parses output format, header style, `noident`, and destination.

Control flow and state: `MP` accumulates multi-line monitor directives, with `...` continuing prior state. Destination-dependent mode bits are merged and duplicate destinations are coalesced. `gsObj` is static global stream configuration and persists until `ConfigGStream()` materializes stream objects.

Dependencies and integration: uses `XrdXrootdMonitor`, `XrdXrootdGSReal`, `XrdXrootdTpcMon`, `XrdNetAddr`, `XrdOucEnv`, and numeric parsers. Plugins can retrieve g-stream pointers from the environment.

Risks and test signals: parser behavior is stateful across continuation lines and supports two destination slots only. Tests should cover duplicate destinations, invalid endpoints, `fstat ssq` on non-IEEE platforms, implied `files` when `io` is selected, all g-stream selection, no-header send formats, and environment publication for HTTP/TPC streams.
