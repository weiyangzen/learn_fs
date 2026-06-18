# sources/distributed-fs/xrootd/src/XrdCms/XrdCmsRedirLocal.hh

Purpose: declares the local redirect CMS client plugin and forwards most `XrdCmsClient` behavior to a native remote finder.

Important APIs/types: constructor/destructor, `Configure`, `loadConfig`, `Locate`, `Space`, forwarding wrappers for `Added`, `Forward`, `isRemote`, `Managers`, `Prepare`, `Removed`, `Resume`, `Suspend`, `Resource`, `Reserve`, and `Release`. Public state includes the wrapped `nativeCmsFinder`, configuration flags, `localroot`, and logger.

Control flow: only `Locate()` and configuration are custom; all other CMS client functions delegate to the native finder to preserve normal CMS behavior.

State and persistence: plugin instance owns `nativeCmsFinder` and configuration values. No persistent data is written.

Dependencies/integration: includes CMS finder/client, network address, OSS, OUC env/stream/string, SFS flags, version metadata, C++ `string`, and `fcntl.h`.

Risks: wrapper methods assume `nativeCmsFinder` is non-null. Public data members make mutation possible outside the class. Header README says readonly default is false, while constructor initializes `readOnlyredirect(true)`, so documentation/config expectations should be reconciled.

Test signals: compile/plugin ABI tests, null native finder defensive tests if construction fails, and configuration default tests to pin readonly behavior.
