# sources/distributed-fs/xrootd/src/XrdOssArc/utils/XrdOssArc_MssCom

Purpose: Python command adapter between XrdOssArc and a mass storage system command, defaulting to an `hsi` invocation. It reports online/offline status, saves files, and requests migration/eviction.

Important APIs/functions: `Execute(argvec)` runs the command and captures combined output. `do_Status(path)` runs `ls -X` and parses `(disk)` and `(tape)` sections into booleans. `do_Save()` creates target directories and uploads local archive files via an MSS command string. `do_Evict()` builds a `mig -P` request for paths but currently does not return or check the result. `Main()` supports `evict`, `offline`, `online`, `save`, and `status`; boolean returns are used as process exit statuses, so `online` returns 1 when on disk and 0 when not.

State/persistence: changes MSS state through save/evict commands. `MSS_CMD` and `MSS_ROOT` come from `XRDOSSARC_MSSCMD` and `XRDOSSARC_MSSROOT`, with site-specific defaults.

Dependencies/integration: `XrdOssArcStage::isOnline()` consumes the `online` exit code through `XrdOucProg`, while `XrdOssArc_Archiver` can use this script as an external saver. Risks include simplistic `split(" ")` for command templates, fragile parsing of `ls -X`, missing `result` initialization if `subprocess.run` raises before assignment, and unchecked evict failures. Tests should mock command output for disk/tape/no-data states and verify exit-code semantics expected by C++ staging.
