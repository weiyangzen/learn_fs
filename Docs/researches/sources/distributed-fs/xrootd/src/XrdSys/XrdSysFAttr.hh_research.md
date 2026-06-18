## sources/distributed-fs/xrootd/src/XrdSys/XrdSysFAttr.hh

Purpose: declares `XrdSysFAttr`, the internal native extended-attribute provider implementing `XrdSysXAttr`.

Important APIs/types/functions: public static `XrdSysXAttr *Xat` is the active provider pointer; `SetPlugin(XrdSysXAttr *xaP, bool push=false)` replaces or pushes an alternate processor. The constructor/destructor are trivial. Inherited operations `Del`, `Free`, `Get`, `List`, and `Set` are private to force callers through `Xat` or the abstract `XrdSysXAttr` interface.

Control flow: callers do not directly invoke private methods on a `XrdSysFAttr` instance; they use `XrdSysFAttr::Xat->...` so the active implementation can be swapped globally.

State and persistence: only static active-provider state is exposed here. The object itself has no per-instance data.

Dependencies and integration: derives from `XrdSysXAttr`, whose `AList` type and virtual interface define the external contract.

Risks: public mutable static pointer can be changed from any translation unit. The private inheritance implementations make misuse harder but not impossible through friend/global objects.

Test signals: verify callers use `Xat`, compile-time prevention of direct private method calls, plugin install behavior, and ABI stability against `XrdSysXAttr`.
