# sources/distributed-fs/xrootd/src/XrdSsi/XrdSsiDir.hh

Purpose: declares `XrdSsiDir`, the SSI directory wrapper implementing the XRootD SFS directory interface. It is a small ownership and delegation class rather than an SSI directory service.

Important APIs/types: overrides `open()`, `nextEntry()`, `close()`, `FName()`, and `autoStat()`. `copyError()` copies the wrapper error object into a caller-supplied `XrdOucErrInfo`. Constructor forwards user and monitor ID to `XrdSfsDirectory` and initializes `dirP` to null.

Control flow and state: the object is either unopened (`dirP == 0`) or delegates every operation to a real `XrdSfsDirectory`. Destructor deletes `dirP` if present. Private fields are `dirP`, `tident`, and `myEInfo`; `myEInfo` is constructed but the implementation mainly uses inherited `error`.

Dependencies and integration: depends on `XrdSfsInterface.hh` and is instantiated by SSI SFS plumbing. Risks include shallow `tident` storage from constructor input, possible confusion between `error` and `myEInfo`, and lack of reset after `close()` because the delegated object remains allocated. Test signals should include destructor cleanup and error propagation through `copyError()`.
