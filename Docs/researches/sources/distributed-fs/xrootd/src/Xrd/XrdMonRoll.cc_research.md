## sources/distributed-fs/xrootd/src/Xrd/XrdMonRoll.cc

Purpose: implements the small registration facade for monitor roll-up counter sets.

Important APIs/types/functions: static `EOV` terminates deprecated `setMember` arrays. The constructor stores a reference to `XrdMonitor` and clears reserved pointers. `Register(rollType, setName, vector<Item>&)` forwards the vector backing array to `XrdMonitor::Register`. Deprecated `Register(..., setMember[])` converts legacy atomic counter arrays into a heap-allocated `std::vector<Item>` and registers that.

Control flow: plugins or addons create static item vectors or legacy arrays, then call `XrdMonRoll::Register()`. Successful registration leaves item storage available for later formatting by `XrdMonitor`.

State/persistence: no durable persistence. For deprecated arrays, a vector is intentionally leaked on successful registration so the `Item` backing storage remains alive for process lifetime.

Dependencies/integration: depends on `XrdMonitor` for validation and formatting, and on `XrdMonRoll.hh` item definitions.

Risks: vector-based registration requires the caller's vector storage to remain valid until process exit; stack vectors would leave dangling `iVec` pointers. Legacy conversion leaks on success by design but deletes on failure.

Test signals: register vector and legacy sets, verify duplicate names fail in `XrdMonitor`, and ensure formatted output can still read registered items after the registration call returns for static vectors.
