## sources/user-network-fs/gcsfuse/internal/util/util.go

Purpose: General utilities for path resolution, size-unit conversion, and global constants.

Important APIs/types/functions: constants `GCSFUSE_PARENT_PROCESS_DIR`, `MaxMiBsInUint64`, `MaxMiBsInInt64`, `MiB`, `KiB`, `HeapSizeToRssConversionFactor`, `MaxTimeDuration`; functions `GetResolvedPath`, `MiBsToBytes`, `BytesToHigherMiBs`.

Control flow: `GetResolvedPath` returns absolute/empty paths unchanged, expands `~/`, otherwise resolves relative paths against `GCSFUSE_PARENT_PROCESS_DIR` if set or current working directory via `filepath.Abs`. `MiBsToBytes` left-shifts with upper bound panic; `BytesToHigherMiBs` rounds bytes up using integer arithmetic and caps overflow shape.

State and persistence behavior: reads environment and current working directory; no persistence.

Dependencies and integration points: used by child process/config path handling and size limit calculations across gcsfuse.

Risks: `path.IsAbs` is used instead of `filepath.IsAbs`, which matters primarily on non-Unix paths. `MiBsToBytes` panics above supported range. Parent process directory is joined without cleaning.

Test signals: `util_test.go` covers path resolution with/without parent env and unit conversion boundaries; benchmark covers byte-to-MiB conversion.
