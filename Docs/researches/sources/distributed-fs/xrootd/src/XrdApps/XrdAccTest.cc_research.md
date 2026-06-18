<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdApps/XrdAccTest.cc -->
# sources/distributed-fs/xrootd/src/XrdApps/XrdAccTest.cc

Purpose: implements `xrdacctest`, a command-line and interactive harness for testing XRootD authorization policy decisions. It loads the default access authorization object, builds an `XrdSecEntity`, then asks whether operations on one or more paths are allowed or which privilege bits apply.

Important APIs/types/functions: global `Authorize` is an `XrdAccAuthorize`; `Entity` is the mutable `XrdSecEntity` under test; `optab` maps short operation names to `Access_Operation`; `Usage()` prints accepted identity and operation syntax; `SetID()` updates optional identity strings; `ZapEntity()` resets identity fields; `main()` parses global options and initializes `XrdAccDefaultAuthorizeObject()`; `DoIt()` parses per-command identity updates and performs access checks; `cmd2op()` maps operation tokens; `PrivsConvert()` converts `XrdAccPrivCaps` to compact privilege letters.

Control flow: startup sets `Entity.addrInfo`, a synthetic trace identity, exports `XRDINSTANCE`, and initializes the authorization object from `-c` config. If arguments remain, one request is executed. Otherwise stdin is read line-by-line with simple quote handling, parsed into tokens, and sent through `DoIt()`. `DoIt()` accepts either legacy positional `<user> <host>` identity or v2 `-a/-e/-g/-h/-o/-r/-u` identity options, handles `*` as identity reset, maps the operation, resolves host metadata when present, and prints `allowed`, `denied`, or privilege letters per path.

State/persistence: state is process-local. The global `Entity` persists across interactive commands until reset or overwritten, and `Entity.ueid` is incremented for each interactive line. No files are written.

Dependencies/integration: integrates with `XrdAccAuthorize`, `XrdAccConfig`, `XrdAccPrivs`, `XrdSecEntity`, `XrdNetAddr`, `XrdOucEnv`, and `XrdOucStream`. It depends on the access plugin exported by `XrdAccDefaultAuthorizeObject()`.

Risks/test signals: interactive state reuse can surprise tests unless `*` or explicit identity fields are used. `cmd2op()` returns `AOP_Any` after printing an invalid-operation message, so bad operations may still produce privilege output. Tests should cover v1 and v2 identity forms, `none` clearing, quoted paths, single-shot exit status, invalid operations, host resolution failures, and `?` privilege rendering.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdApps/XrdAccTest.cc -->
