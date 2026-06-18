# sources/test-tools/crashmonkey/code/tests/test_get_log_ent_size.c

Purpose: tiny C helper that creates `/mnt/snapshot/test_file` and writes a fixed string, apparently for exercising or estimating log-entry sizes in the disk-wrapper/high-water-mark module. It assumes the kernel module is loaded and running.

Important APIs/types/functions: `open`, `write`, `close`, `strlen`, `printf`, and constants `TEXT` and `TEST_FILE`. It includes ioctl/stat headers but does not actually issue ioctls.

Control flow: `main` opens the test file with `O_RDWR|O_CREAT`, writes until the fixed string length is reached, closes, and returns 0; on open/write failure it prints a message, closes if needed, and returns -1. The `fsync` call is present but commented out.

State/persistence behavior: creates or updates one file under `/mnt/snapshot`; without fsync, persistence is left to normal kernel writeback and any active logging module. Dependencies/integration: likely run manually or by harness code outside the shared-object workload loader.

Risks/test signals: the write loop assigns `written = write(...)` rather than accumulating bytes, so partial writes can produce incorrect offsets or loops; file mode is omitted for `O_CREAT`, which is undefined for the three-argument `open` contract.
