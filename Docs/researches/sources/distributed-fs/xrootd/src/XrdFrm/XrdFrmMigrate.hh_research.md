## sources/distributed-fs/xrootd/src/XrdFrm/XrdFrmMigrate.hh

Purpose: declares the static migration coordinator used by `frm_xfrd` to discover migratable resident files and inject transfer requests. The class has no per-instance state; it is a process-global service.

Important APIs/types: public methods are `Display()` for configuration reporting, `Queue()` for converting an already-selected fileset to a request, and `Migrate()` for starting or running the scanner. Private helpers `Add()`, `Advance()`, `Defer()`, `Eligible()`, and `Scan()` implement screening and deferred-idle handling. Static variables `fsDefer` and `numMig` track the current cycle's deferred files and selected count.

State and persistence: only in-memory cycle state is declared here. Durable eligibility comes from fileset metadata read by `XrdFrmFileset` and fail files checked by transfer code.

Dependencies and integration: forward declares `XrdFrmFileset`, `XrdFrmXfrQueue`, and `XrdOucTList`. It is initialized by `XrdFrmXfrDaemon::Init()` when migratable paths and output copy commands are configured.

Risks and test signals: because the interface is fully static, multiple independent migration policies cannot coexist in one process. Tests should exercise the class as a singleton, including cleanup of deferred files and interactions with transfer queue failures.
