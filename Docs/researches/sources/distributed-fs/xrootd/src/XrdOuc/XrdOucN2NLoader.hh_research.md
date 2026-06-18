<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdOuc/XrdOucN2NLoader.hh -->
# sources/distributed-fs/xrootd/src/XrdOuc/XrdOucN2NLoader.hh

Purpose: Declares the helper that instantiates name translation plugins from `oss.namelib`/proxy configuration state.

APIs and control flow: The constructor uses `XrdOucgetName2NameArgs` to capture the error route, config filename, plugin parameters, local root, and remote root. `Load()` accepts a library name, caller version, and optional environment to receive the vector translator pointer.

State and persistence: Stores borrowed pointers only; it does not own or copy configuration strings. Plugin and mapper lifetime are established by `Load()` and its dependencies.

Dependencies and integration: Includes `XrdOucName2Name.hh` for the plugin factory signature and mapper type, and forward-declares `XrdOucEnv` and `XrdVersionInfo`.

Risks and test signals: Because constructor arguments are borrowed, callers must keep them alive through `Load()`. Tests should compile third-party plugin users against this header and validate both built-in and plugin loader call signatures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdOuc/XrdOucN2NLoader.hh -->
