# sources/distributed-fs/xrootd/src/XrdSsi/XrdSsiEvent.hh

Purpose: declares `XrdSsiEvent`, an abstract base that adapts XRootD client responses into SSI scheduler jobs. Subclasses implement the actual event execution and completion hooks.

Important APIs/types: public `AddEvent()`, `ClrEvent()`, `DoIt()`, and `HandleResponse()` implement the queueing/dispatch contract. Subclasses must implement `XeqEvent(XrdCl::XRootDStatus *, XrdCl::AnyObject **)` and `XeqEvFin()`. The nested `EventData` stores one status/response pair and a next pointer; `Move2()` transfers ownership without copying payloads.

Control flow and state: `HandleResponse()` simply calls `AddEvent()`. `DoIt()` is invoked by the scheduler, not directly by the client callback. Protected `tident` is wired to `XrdJob::Comment` for trace output. Destructor clears pending events when the object is not already clear.

Dependencies and integration: depends on `XrdJob`, `XrdClXRootDResponses`, and `XrdSsiAtomics` for mutex helpers. Risks include subclass obligations: `XeqEvent()` must respect ownership of `response` and return negative only when the object is unsafe to touch. Test signals should use a fake subclass to assert event order, callback-to-scheduler transition, and cleanup after early halt.
