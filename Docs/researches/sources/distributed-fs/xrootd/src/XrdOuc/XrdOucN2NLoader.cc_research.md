<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdOuc/XrdOucN2NLoader.cc -->
# sources/distributed-fs/xrootd/src/XrdOuc/XrdOucN2NLoader.cc

Purpose: Loads the configured logical-name to physical-name translator, either the built-in default mapper or a shared-library plugin.

APIs and control flow: `Load()` first handles the default path when `libName` is null: it compares version metadata, validates `lclRoot` as a directory, exports `XRDLCLROOT`/`XRDRMTROOT`, calls built-in `XrdOucgetName2Name()`, and stores the optional vector mapper in the environment. For plugin mode it exports `XRDN2NLIB` and `XRDN2NPARMS`, uses `XrdOucPinLoader` to resolve `XrdOucgetName2Name`, constructs the mapper, and optionally resolves `?Name2NameVec`.

State and persistence: Loader instances borrow constructor arguments. Loaded plugin images are managed by `XrdOucPinLoader`; returned mapper objects are owned by the caller. Environment exports are process-wide.

Dependencies and integration: Bridges `XrdOucName2Name`, `XrdOucPinLoader`, `XrdSysPlugin`, version metadata, and configuration environments.

Risks and test signals: Root validation and version compatibility are startup-critical. Tests should cover null library default mapping, invalid local root, plugin symbol absence, optional vector symbol, and exported environment values.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdOuc/XrdOucN2NLoader.cc -->
