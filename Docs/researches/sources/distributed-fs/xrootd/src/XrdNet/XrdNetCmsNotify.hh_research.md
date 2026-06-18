## sources/distributed-fs/xrootd/src/XrdNet/XrdNetCmsNotify.hh

Purpose: Declares the CMS notification helper that reports file presence/removal events.

Important APIs and types: Public methods `Have` and `Gone`; option bits `isServ` and `noPace`; constructor and destructor. Private `Send` centralizes pacing and transport.

Control flow: Header defines a simple command-oriented API; implementation maps calls to text datagrams.

State and persistence: Holds raw pointers to `XrdSysError`, `XrdNetMsg`, and duplicated destination path plus pacing flag. No persistence beyond process memory.

Dependencies and integration points: Forward declares `XrdNetMsg` and `XrdSysError`. Used by server/cache-manager integration code that needs to notify olbd.

Risks: Raw pointer ownership is split: logger is non-owned, message and path are owned. Copying is not disabled, so accidental copies would double-free.

Test signals: Compile construction in CMS code; avoid copying in callers; verify option bits remain stable for configuration code.
