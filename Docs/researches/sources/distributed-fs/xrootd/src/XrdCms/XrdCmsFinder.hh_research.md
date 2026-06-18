# sources/distributed-fs/xrootd/src/XrdCms/XrdCmsFinder.hh

Purpose: declares the two concrete CMS finder classes used through the `XrdCmsClient` interface: remote manager-facing finder `XrdCmsFinderRMT` and target cmsd-facing finder `XrdCmsFinderTRG`.

Important APIs/types/functions: `XrdCmsFinderRMT` exposes file-location, prepare, forwarding, space, manager listing, and version-check methods. Its private surface contains manager selection, two-way sends, local locate formatting, manager startup, and broadcast inform helpers. `XrdCmsFinderTRG` exposes file add/remove notifications, local locate, perf/resource reporting, suspend/resume, resource reservation, admin startup, and performance monitor execution while privately handling cmsd hookup and request processing.

Control flow: the header separates client roles at type level. Remote instances configure outbound `XrdCmsClientMan` manager connections and submit packed CMS requests. Target instances configure a local cmsd admin channel and report state/load/file changes upward. Both provide `Managers()` for configuration consumers and static `VCheck()` for plugin compatibility.

State and persistence behavior: `XrdCmsFinderRMT` owns manager tables/lists, configuration wait intervals, mode flags, and selector behavior. `XrdCmsFinderTRG` owns an `XrdOss*`, cmsd socket stream, login line, active state, resource counters, and optional perfmon pointer/interval. State is in-memory and tied to daemon lifetime.

Dependencies: depends on `XrdCmsClient`, `XrdCmsPerfMon`, pthread mutexes, SFS prep types, OSS, OUC env/error/list types, and version info. It forward-declares most heavy types to reduce include pressure.

Integration points: included by client factory code, local redirector support, and components needing CMS manager lists or target perfmon reporting. The class methods implement the public CMS client contract used by xrootd storage and redirector logic.

Risks: header exposes raw pointers and manual ownership semantics for manager lists, `CMSPath`, `Login`, and stream pointers. The two classes share method names but very different semantics, so callers must instantiate the right role. `MaxMan` is a hard cap. Resource counters are protected by `rrMutex`, but active stream writes require consistent `myData` locking in the implementation.

Test signals: compile tests for plugin ABI, construction in all role modes, manager list ownership, local/remote `Locate()` behavior, `Managers()` lifetime, and version compatibility checks.
