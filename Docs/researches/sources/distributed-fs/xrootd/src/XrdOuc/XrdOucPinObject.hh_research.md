<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdOuc/XrdOucPinObject.hh -->
# sources/distributed-fs/xrootd/src/XrdOuc/XrdOucPinObject.hh

Purpose: Defines the object-oriented plugin factory interface used by `XrdOucPinKing`.

APIs and control flow: Template interface `XrdOucPinObject<T>::getInstance()` receives plugin parameters, the process/config environment, logger, and an optional previous plugin instance for stacking. It returns a concrete `T*`.

State and persistence: The interface itself is stateless. Implementations in plugin shared libraries determine instance ownership and any persistent state.

Dependencies and integration: Forward-declares `XrdOucEnv` and `XrdSysLogger`. Plugin libraries export a symbol whose object derives from this template specialization.

Risks and test signals: ABI compatibility depends on template specialization, symbol naming, and matching `T`. Tests should load a sample object plugin, verify stacked `prevP` behavior, parameter passing, logger use, and null returns on initialization failure.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdOuc/XrdOucPinObject.hh -->
