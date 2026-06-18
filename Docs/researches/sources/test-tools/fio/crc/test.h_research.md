# sources/test-tools/fio/crc/test.h

Purpose: Provides the small public declaration for fio's checksum benchmark command.

Important APIs/types: Exports `int fio_crctest(const char *type);`, where `type` is null for all algorithms, `help`/`list` for names, or a comma-separated subset.

Control flow: Consumers include the header and dispatch to `fio_crctest()`; all parsing and printing are handled in `test.c`.

State/persistence: No state is declared here.

Dependencies/integration: Guarded by `FIO_CRC_TEST_H`; consumed by fio command-line/test plumbing.

Risks: The header does not describe accepted names or side effects, so callers must rely on `test.c` behavior.

Test signals: A build that includes the benchmark should link exactly one `fio_crctest()` implementation and expose list/help behavior.
