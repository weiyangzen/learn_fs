## sources/distributed-fs/xrootd/src/XrdHttp/XrdHttpModule.cc

Purpose: provides the dynamically loaded HTTP protocol module entry points required by the XRootD protocol driver.

Important APIs and control flow: `XrdVERSIONINFO(XrdgetProtocol, xrdhttp)` declares version metadata for the protocol factory. `XrdgetProtocol()` logs initialization banners, calls `XrdHttpProtocol::Configure(parms, pi)`, returns a new `XrdHttpProtocol(false)` on success, and logs completion/failure. `XrdVERSIONINFO(XrdgetProtocolPort, xrdhttp)` marks the port callback. `XrdgetProtocolPort()` returns default HTTP/XRootD port `1094` when `pi->Port < 0`, otherwise returns the configured port.

State and persistence: no persistent state is owned here; module loading allocates a protocol object and relies on `XrdHttpProtocol` static configuration.

Dependencies and integration: compiled as the `XrdHttp-${PLUGIN_VERSION}.so` module. It includes `XrdVersion.hh` and `XrdHttpProtocol.hh` and exposes C symbols expected by XRootD.

Risks and test signals: module ABI depends on exact extern "C" symbol names and version macros. Tests should load the plugin through the protocol loader, verify failure when configuration fails, verify banner logging, and check port default/override behavior.
