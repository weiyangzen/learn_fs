## sources/distributed-fs/xrootd/src/Xrd/XrdLinkCtl.hh

Purpose: declares the static control plane for `XrdLink` lifecycle management. The class is a protected subclass of `XrdLinkXeq`, allowing allocated table entries to be used as public `XrdLink` objects while exposing only static management APIs.

Important APIs/types/functions: `Alloc()` creates/reuses a link for an accepted peer. `fd2link()` and `fd2PollInfo()` translate active fds to runtime objects. `Find()` and `getName()` scan active links. `idleScan()`, `setKWT()`, `Setup()`, `SyncAll()`, and `Unhook()` manage runtime maintenance. `RegisterCloseRequestCb()` allows a protocol to intercept self-close requests. `XRDLINK_RDLOCK` and `XRDLINK_NOCLOSE` tune read serialization and fd ownership.

Control flow: setup initializes tables before network accepts. Accept paths allocate links, pollers use `fd2PollInfo`, protocols/admin tools use `Find`, and close paths call `Unhook`.

State/persistence: declares static table state: `LTMutex`, `LinkTab`, `LinkBat`, `LinkAlloc`, `LTLast`, `maxFD`, and kill timing constants. State is memory-only and process-wide.

Dependencies/integration: depends on `XrdLinkXeq`, `XrdSysPthread`, and `XrdLinkMatch`; it is tightly coupled to the executor object layout because table entries are actual `XrdLinkCtl` instances.

Risks: inheritance and casts depend on stable class layout. Inline fd lookup accepts negative fds by taking absolute value; callers must avoid passing sentinel negatives that should not resolve. `LinkBat` is the authoritative active flag, so every close path must call `Unhook()`.

Test signals: compile and runtime tests should validate fd lookup, fd+instance lookup, poll info lookup, close callback registration failure for null links, and kill wait configuration.
