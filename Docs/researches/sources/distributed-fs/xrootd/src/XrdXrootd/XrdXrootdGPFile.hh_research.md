# sources/distributed-fs/xrootd/src/XrdXrootd/XrdXrootdGPFile.hh

Purpose: declares the get/put-file plugin interface used by XRootD to hand whole-file copy requests to an optional external implementation. The header defines the request argument/callback carrier and the abstract `XrdXrootdGPFile` service with `getFile()` and `putFile()` entry points.

Important APIs/types/functions: `XrdXrootdGPFileInfo` carries checksum type/value, source and destination strings, CGI fragments, ping interval, and stream count. Its `Completed()` callback reports terminal success or an errno/message pair, while `Update()` reports transferred bytes and status (`isPending`, `isCopying`, `isProving`). `XrdXrootdGPFile` is the plugin base class, and `XrdOfsgetPrepare_t` plus `XrdOfsgetPrepareArguments` define the shared-library factory ABI.

Control flow: the xrootd command path constructs an info object bound to an `XrdXrootdGPFAgent`, loads a plugin factory, calls either `getFile()` or `putFile()`, and expects the plugin to signal all acceptance, progress, and final outcomes through the `XrdXrootdGPFileInfo` callbacks. The call may be accepted asynchronously; completion must delete or retire the info object after `Completed()`.

State and persistence behavior: this header owns no persistent storage. State is request-scoped in `XrdXrootdGPFileInfo` and plugin-owned after dispatch. Persistent effects are external file transfers and optional checksum verification performed by the plugin.

Dependencies: forward-declares `XrdOucEnv`, `XrdOucErrInfo`, `XrdSecEntity`, `XrdSfs`, and `XrdXrootdGPFAgent`; the factory ABI also uses `XrdSysError`. It integrates with the server filesystem plugin and security identity passed to copy plugins.

Integration points: loaded by xrootd configuration/plugin machinery. Implementers are expected to export a C factory and `XrdVERSIONINFO` so server/plugin ABI mismatches can be detected.

Risks: the listed source contains apparent declaration inconsistencies: `srcCgi` is declared twice where the second field is documented as destination CGI, the constructor initializes `dstCgi`, and `pingsec`/`pingSec` spelling differs. As written, that is a compile/API risk unless a local patch or preprocessor context fixes it. Callback lifetime is also delicate because the object must survive asynchronous transfer but be deleted after completion.

Test signals: compile a minimal plugin against the header; load success/failure paths for the factory; rejected transfer calls `Completed(errno)`; progress pings at `pingsec`; checksum requested and omitted cases; disconnected client causing callback false returns; ABI version mismatch handling.
