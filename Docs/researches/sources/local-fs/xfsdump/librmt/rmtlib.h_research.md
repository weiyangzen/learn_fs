# File Research: sources/local-fs/xfsdump/librmt/rmtlib.h

Private header for `librmt`.

Defines:
- `REM_BIAS` descriptor bias for remote descriptors.
- `BUFMAGIC` command/status buffer size.
- `MAXUNIT` maximum remote tape units, set to 4.
- Macros for read/write pipe arrays and remote host table.
- Default `RSH_PATH` and `RMT_PATH`.
- Remote host IDs for Linux, IRIX, unknown, and undefined.
- Message levels and prototypes.

Exports globals:
- `_rmt_Ctp[MAXUNIT][2]`
- `_rmt_Ptc[MAXUNIT][2]`
- `_rmt_host[MAXUNIT]`

Role:
- Defines the remote descriptor model and shared protocol support primitives for all wrapper files.
