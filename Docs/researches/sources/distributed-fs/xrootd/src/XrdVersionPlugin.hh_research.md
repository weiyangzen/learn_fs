# sources/distributed-fs/xrootd/src/XrdVersionPlugin.hh

Purpose: Defines plugin version-checking rules, strict versioned plugin library names, and directive-to-plugin-symbol mappings for XRootD plugin loading.

Important APIs/types/functions: XrdVersionPlugin describes a creator symbol name/prefix/suffix, processing mode, and minimum compatible major/minor versions. Macros define DoNotChk, Optional, Required, XrdVERSIONPLUGIN_Rule, XrdVERSIONPLUGINRULES, XrdVERSIONPLUGIN_Maxim, XrdVERSIONPLUGINMAXIMS, XrdVERSIONPLUGINSTRICT, XrdVersionMapD2P, XrdVERSIONPLUGIN_Mapd, and XrdVERSIONPLUGINMAPD2P.

Control flow: XrdSysPlugin.cc consumes these macro-expanded tables to decide whether a loaded plugin must have version info, whether missing info is warning/fatal, and how directives map to creator symbols.

State/persistence: Static compile-time table data only.

Dependencies/integration: Includes entries for security, HTTP, storage, checksum, cache, XrdCl, VOMS, throttle, and other plugins. VOMS-specific entries include XrdSecgsiVOMSFun, XrdSecgsiVOMSInit, and strict libraries libXrdSecgsiVOMS.so/libXrdVoms.so.

Risks: Any plugin interface ABI change must update these rules. Missing strict names can allow unversioned fallback where not intended. New directives must be added to the mapping table to get correct loader diagnostics.

Test signals: Plugin loader tests for required/optional/missing version info, strict library name fallback rejection, directive mapping, and future major/minor compatibility boundaries.
