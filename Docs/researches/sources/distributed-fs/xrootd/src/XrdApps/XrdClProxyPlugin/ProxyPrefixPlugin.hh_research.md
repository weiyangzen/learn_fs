<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdApps/XrdClProxyPlugin/ProxyPrefixPlugin.hh -->
# sources/distributed-fs/xrootd/src/XrdApps/XrdClProxyPlugin/ProxyPrefixPlugin.hh

Purpose: declares `xrdcl_proxy::ProxyFactory`, the XrdCl plugin factory for creating `ProxyPrefixFile` instances.

Important APIs/types/functions: `ProxyFactory` derives from `XrdCl::PlugInFactory`; it has a config-map constructor, virtual destructor, `CreateFile(const std::string&)`, and `CreateFileSystem(const std::string&)`.

Control flow: XrdCl plugin loading constructs this factory through the exported C symbol in the `.cc` file; callers then request file plugins per URL. The header does not store config state.

State/persistence: no data members and no durable state; all side effects are implemented in the constructor in the `.cc` file.

Dependencies/integration: depends on `XrdCl/XrdClPlugInInterface.hh` and the XrdCl plugin factory lifecycle.

Risks/test signals: the factory ignores the URL parameter when creating files and does not support filesystem plugins. Tests should compile against the current `PlugInFactory` virtual signatures and verify file plugin construction through the exported loader path.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdApps/XrdClProxyPlugin/ProxyPrefixPlugin.hh -->
