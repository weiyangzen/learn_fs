# sources/distributed-fs/xrootd/src/XrdCks/XrdCksConfig.cc

Purpose: implements checksum manager configuration, including default manager creation, manager override loading, calculator library directive parsing, and stackable checksum plugins.

Important APIs: the constructor verifies version compatibility. `Configure()` obtains a manager with `getCks()`, stacks `XrdCksAdd2` plugins via `addCks()`, applies queued `ckslib` config lines, and calls `Init()`. `getCks()` returns `XrdCksManOss` when an OSS object is supplied, `XrdCksManager` otherwise, or loads a custom manager library with `XrdCksInit`. `Manager()` replaces custom manager path/parameters. `ParseLib()` parses `ckslib <digest> <path> [parms]`, with `*` for manager override, `=` for default manager selection, and `++` for stackable plugins. `ParseOpt()` accepts default manager option `nomtchk`.

Control flow: configuration directives are accumulated in linked lists, then consumed when `Configure()` creates the manager. Pin loaders intentionally keep shared libraries open while discarding loader objects.

State and persistence: stores config filename, custom manager path/parameters, digest config list, stackable library list, version info, and checksum manager options. No checksum values are persisted here.

Dependencies and integration: depends on `XrdCksManager`, `XrdCksManOss`, `XrdCksWrapper`, `XrdOucPinLoader`, `XrdOucStream`, plugin version APIs, and XRootD utility lists.

Risks and test signals: directive parsing tests should cover missing digest/path, too-long fields, `default` restrictions, manager replacement, `++` stack order, invalid options, and plugin symbol failures. Memory ownership for `strdup` paths and linked lists should be leak-checked.
