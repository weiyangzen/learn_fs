# sources/test-tools/xfstests-bld/fstests-bld/e2fsprogs-libs/lib/uuid/uuidd.h

Purpose: `uuidd.h` defines constants and private generator hooks used by the `uuidd` daemon protocol.

Important APIs, types, and functions: daemon paths `UUIDD_DIR`, `UUIDD_SOCKET_PATH`, `UUIDD_PIDFILE_PATH`, and `UUIDD_PATH`; operation constants `UUIDD_OP_GETPID`, `UUIDD_OP_GET_MAXOP`, `UUIDD_OP_TIME_UUID`, `UUIDD_OP_RANDOM_UUID`, `UUIDD_OP_BULK_TIME_UUID`, `UUIDD_OP_BULK_RANDOM_UUID`, and `UUIDD_MAX_OP`; private functions `uuid__generate_time(uuid_t out, int *num)` and `uuid__generate_random(uuid_t out, int *num)`.

Control flow: header-only preprocessor definitions, with an include guard. No runtime flow.

State and persistence: defines filesystem locations under `/var/lib/libuuid` for the daemon socket and pidfile. Those paths are persistent integration points for daemon/client coordination.

Dependencies and integration points: includes or relies on `uuid_t` being available from the public UUID headers in compilation units that include it. The operation codes must match uuidd client/server implementations elsewhere in libuuid/e2fsprogs.

Risks: hard-coded paths may not match downstream packaging policies. Operation-code changes are protocol-breaking. The closing include-guard comment says `_UUID_UUID_H`, which appears copied from another header and is misleading.

Test signals: daemon/client integration tests should validate socket path use, op code dispatch, and bulk UUID generation counts. Header compile tests catch missing `uuid_t` include ordering.
