# sources/distributed-fs/xrootd/src/XrdOuc/XrdOucTPC.hh

Purpose: declares the static utility interface for third-party-copy CGI parameter construction and filtering.

Important APIs, types, and functions: public methods are `cgiC2Dst()`, `cgiC2Src()`, `cgiD2Src()`, and `copyCGI()`. Public static string constants name CGI keys such as `tpc.key`, `tpc.src`, `tpc.dst`, `tpc.ttl`, and `tpc.dlgon`. Private `tpcInfo` stores parsed user/host/port fragments, and `cgiHost()` performs normalization.

Control flow: callers choose the helper based on copy direction and role, provide a caller-owned output buffer, and receive either that buffer or a string beginning with `!` describing invalid parameters or generation failure.

State and persistence: no instance state exists. Static key strings are read-only process globals.

Dependencies and integration points: includes `<cstdlib>` for `free()` in `tpcInfo` destructor and integrates with TPC protocol and CGI handling code.

Risks and test signals: error signaling as a string pointer requires callers to check for leading `!` rather than errno/status. Tests should verify all declared static key names match protocol expectations and are initialized by the `.cc`.
