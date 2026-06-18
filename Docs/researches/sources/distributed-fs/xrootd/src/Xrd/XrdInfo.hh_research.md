<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/Xrd/XrdInfo.hh -->
# sources/distributed-fs/xrootd/src/Xrd/XrdInfo.hh

Purpose: defines basic Xrd format/version/banner constants used by startup and informational output.

Important APIs/types/functions: includes `XrdVersion.hh`, defines `XrdFORMAT`, `XrdFORMATB`, and `XrdBANNER`.

Control flow: no runtime flow.

State and persistence behavior: compile-time constants only. `XrdFORMATB` is assigned to `XrdProtocol_Config::Format` during configuration, and `XrdBANNER` is logged during startup.

Dependencies: `XrdVersion.hh` supplies `XrdVSTRING` and related version macros.

Integration points: used by `XrdConfig.cc` for banner logging and protocol config format compatibility. Any protocol plugin receiving `ProtInfo` may inspect the format.

Risks: version/format constants must change only with compatible runtime expectations. `XrdBANNER` contains a fixed copyright range and dynamic version string.

Test signals: compile tests; startup log assertions; plugin compatibility checks on `ProtInfo.Format`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/Xrd/XrdInfo.hh -->
