<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdApps/XrdClRecordPlugin/XrdClRecorderPlugin.cc -->
# sources/distributed-fs/xrootd/src/XrdApps/XrdClRecordPlugin/XrdClRecorderPlugin.cc

Purpose: provides the C ABI entry point used by XrdCl to load the recorder plugin.

Important APIs/types/functions: includes `XrdClRecorder.hh` and `XrdClRecorderPlugin.hh`; `XrdVERSIONINFO(XrdClGetPlugIn, XrdClGetPlugIn)` exposes version metadata; extern "C" `XrdClGetPlugIn(const void*)` casts the config pointer to `std::map<std::string,std::string>` and returns a new `XrdCl::RecorderFactory`.

Control flow: XrdCl dynamically loads the shared library, resolves `XrdClGetPlugIn`, passes plugin config, and receives a factory that can create recorder file plugins.

State/persistence: this file has no state beyond allocating the factory. Output-file state is configured by the factory/header implementation.

Dependencies/integration: integrates with the XrdCl plugin loader ABI, `XrdVersion`, and `RecorderFactory`.

Risks/test signals: the entry point assumes the opaque config pointer, when non-null, has the expected map type. Tests should validate dynamic loading, version symbol availability, null config handling, and factory lifetime cleanup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdApps/XrdClRecordPlugin/XrdClRecorderPlugin.cc -->
