# sources/test-tools/crashmonkey/code/tests/generic_042/generic_042_base.h

Purpose: declaration for the generic/042 shared base class. It defines the constructor parameters and protected verification helpers used by all fallocate/zero/punch subclasses.

Important APIs/types/functions: `Generic042Base` inherits `BaseTestCase`; declares `setup()`, `run(int checkpoint)`, pure virtual `check_test`, constructor `(start_file_size, falloc_offset, falloc_len, mode)`, and helpers `CheckBase`, `CheckDataNoZeros`, `CheckDataWithZeros`, `ReadData`, and `HexdumpFile`.

Control flow: the header enforces a template method shape: subclasses only supply `check_test()` and constructor constants while the base handles setup and run.

State/persistence behavior: stores immutable `start_file_size_`, `falloc_offset_`, `falloc_len_`, and `falloc_mode_` used for workload state and recovery checks.

Dependencies/integration: includes `../BaseTestCase.h` and `cstdint`; exposes helper methods to derived source files in the same directory.

Risks/test signals: because `check_test()` remains pure virtual, each derived workload must choose the correct zero/nonzero expectations. A mismatch in constructor constants directly changes the persistence oracle.
