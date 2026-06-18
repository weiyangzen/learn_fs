<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdApps/XrdClProxyPlugin/ProxyPrefixPlugin.cc -->
# sources/distributed-fs/xrootd/src/XrdApps/XrdClProxyPlugin/ProxyPrefixPlugin.cc

Purpose: exports the XrdCl plugin entry point and implements `ProxyFactory`, which creates proxy-prefix file plugins and maps plugin configuration values into environment variables consumed by `ProxyPrefixFile`.

Important APIs/types/functions: `XrdVERSIONINFO(XrdClGetPlugIn, XrdClGetPlugIn)` publishes version metadata; extern "C" `XrdClGetPlugIn(const void*)` casts the config map and returns `new ProxyFactory`; `ProxyFactory::ProxyFactory()` reads selected keys and calls `setenv(..., overwrite=0)`; `CreateFile()` returns a new `ProxyPrefixFile`; `CreateFileSystem()` logs unsupported status and returns null.

Control flow: plugin loading calls `XrdClGetPlugIn()`, construction optionally exports `XROOT_PROXY`, `xroot_proxy`, `XROOT_PROXY_EXCL_DOMAINS`, and `xroot_proxy_excl_domains` if present and non-empty, then XrdCl asks the factory for per-URL file plugins.

State/persistence: mutates process environment, intentionally not overwriting existing variables. No filesystem persistence.

Dependencies/integration: integrates with the XrdCl plugin loader ABI, `XrdVersion`, `XrdCl::PlugInFactory`, `XrdCl::DefaultEnv` logging, and `ProxyPrefixFile`.

Risks/test signals: using process-wide environment variables means multiple plugin instances or concurrent users share configuration. Lowercase `xroot_proxy_excl_domains` is exported but `ProxyPrefixFile::GetExclDomains()` reads only uppercase `XROOT_PROXY_EXCL_DOMAINS`, so lowercase exclusion config is ineffective. Tests should cover config-to-env mapping, no-overwrite behavior, factory creation, unsupported filesystem plugin, and mixed upper/lowercase config keys.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdApps/XrdClProxyPlugin/ProxyPrefixPlugin.cc -->
