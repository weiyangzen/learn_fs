# sources/distributed-fs/xrootd/src/XrdOss/XrdOssStatInfo.hh

Purpose: defines the plug-in ABI for replacing or augmenting OSS stat behavior, including optional file-add/remove event relay for cmsd server mode.

Important APIs/types/functions: `XrdOssStatEvent::{FileAdded,PendAdded,FileRemoved}`, function pointer types `XrdOssStatInfo_t` and `XrdOssStatInfo2_t`, and initialization typedefs `XrdOssStatInfoInit_t` and `XrdOssStatInfoInit2_t`.

Control flow: the header describes two call forms. V1 receives path, stat buffer, options, and environment; V2 additionally receives the logical filename. For event relay, `buff == 0` signals a set/event operation rather than a query, and `opts` is one of the event constants.

State and persistence behavior: no local state. Plug-ins can read external metadata or update external state when event relay is enabled. Returned stat structures influence OSS file visibility and attributes.

Dependencies: forward declarations for `XrdOss`, `XrdOucEnv`, `XrdSysLogger`, and `struct stat`. Plug-ins are loaded through `oss.statlib` and must expose C linkage plus `XrdVERSIONINFO`.

Integration points: `XrdOssSys::Stat()` preferentially uses this ABI when configured. cmsd/xrootd/frm context is communicated through `XRDPROG` and `XRDROLE` environment variables.

Risks: ABI stability matters for external shared libraries; V1/V2 mismatch will fail initialization or pass incomplete context; return convention is `-1` with `errno`, unlike many internal XRootD APIs that return `-errno`; event return values are not inspected.

Test signals: load v1 and v2 plug-ins, verify logical-name parameter, failure errno propagation, arevents mode, version info enforcement, and environment context for cmsd/xrootd roles.
