# sources/user-network-fs/nfs-ganesha/src/Protocols/RQUOTA/CMakeLists.txt

Purpose: builds the optional RQUOTA protocol object library.

Important APIs/types/functions: defines `rquota_STAT_SRCS` with null, getquota, getactivequota, setquota, setactivequota, and common helpers; creates `rquota` object target with sanitizers and `-fPIC`; optionally depends on generated LTTng trace headers.

Control flow: parent protocol build enters this directory when `USE_RQUOTA` is enabled. The object library is compiled and later linked into the server.

State and persistence: no runtime state; only build target metadata.

Dependencies and integration points: integrates with `Protocols/CMakeLists.txt`, generated tracing, and all RQUOTA procedure symbols used by dispatch/XDR code.

Risks and test signals: the source list includes `rquota_setquota.c` even though it is outside this work item, so build validation should cover the complete target. Test enabled/disabled RQUOTA builds, sanitizer builds, LTTng builds, and link resolution for all RQUOTA procedures.
