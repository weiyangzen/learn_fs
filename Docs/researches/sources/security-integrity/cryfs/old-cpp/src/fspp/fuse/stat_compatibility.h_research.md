# sources/security-integrity/cryfs/old-cpp/src/fspp/fuse/stat_compatibility.h

Purpose: small platform compatibility header that gives fspp FUSE code a single `fspp::fuse::STAT` type across POSIX FUSE and Windows Dokan.

Important APIs/types/functions: namespace `fspp::fuse`, typedef `STAT`, `_MSC_VER` branch, `FUSE_STAT`, and POSIX `struct stat`.

Control flow: preprocessor selects Dokan/FUSE's `FUSE_STAT` under MSVC and `::stat` elsewhere.

State and persistence behavior: no state; this is an ABI/typing shim used by code that fills stat structures.

Dependencies and integration points: includes `<fuse.h>` on MSVC and `<sys/stat.h>` otherwise. It is consumed by FUSE adapter code that wants one stat spelling.

Risks and test signals: correctness depends on Dokan's `FUSE_STAT` being layout-compatible with expected stat fields. Non-MSVC Windows compilers would take the POSIX branch, which may be wrong for Dokan builds.
