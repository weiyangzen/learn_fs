# sources/distributed-fs/xrootd/src/XrdApps/XrdMpxXml.hh

Purpose: declares the lightweight statistics XML formatter used by XRootD command-line stats tools.

Important APIs/types/functions: `XrdMpxXml::fmtType` selects `fmtCGI`, `fmtFlat`, `fmtText`, or `fmtXML`; the constructor derives separator/suffix behavior and enables human variable-name translation for text; public `Format(const char *Host, char *ibuff, char *obuff)` converts one mutable input XML buffer into the provided output buffer.

Control flow: callers instantiate only when they need non-XML output. `Format` delegates to private helpers `Add`, `getVars`, and `xmlErr`; headers and stack logic live in the `.cc`.

State and persistence: each object stores format flags (`fType`, `vSep`, `vSfx`, `Debug`, `noZed`, `doV2T`). There is no persistent state, but `Debug` and `noZed` affect every conversion through the object.

Dependencies and integration points: forward-declares `XrdOucTokenizer` and is included by `XrdMpxStats.cc` and `XrdQStats.cc`. It is not a general XML API; it is coupled to the XRootD statistics XML shape.

Risks: the constructor parameter name `nz` is used both as no-zero suppression and, in one caller, as debug-only context; users must understand the exact signature. `fmtXML` is declared but the converter object is normally not created for XML passthrough. `Format` has no output length parameter.

Test signals: compile-time coverage of all enum values, constructor behavior for separator/suffix, zero suppression in text mode, and callers passing mutable buffers of sufficient size.
