# sources/test-tools/syzkaller/tools/syz-declextract/testdata/io_uring.c.json

Purpose: this golden JSON records expected extraction for the io_uring table fixture.

Important structure: top-level keys are `functions`, `consts`, and `iouring_ops`. Functions include all prep and issue callbacks. Constants include NOP, READV, WRITEV, and NOT_SUPPORTED with values 0 through 3. `iouring_ops` maps NOP to `io_nop`, READV to `io_read`, and WRITEV to `io_write`.

State and persistence: static clang-cache input for tests; it must track source line numbers and enum values.

Dependencies and integration: consumed by `TestDeclextract` to validate generated descriptions and interface info.

Risks and test signals: catches regressions in indexed initializer parsing and unsupported-op filtering. It does not cover SQE argument structures or real kernel io_uring complexity.
