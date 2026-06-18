# File Research: sources/virtualization/nvme-cli/tests/nvme_test_logger.py

Simple stdout/stderr tee logger for Python tests.

Key elements:
- Stores the original `sys.stdout` in `terminal`.
- Opens a log file for writing.
- `write` sends every message to both terminal and log file.
- `flush` is a no-op for Python 3 compatibility.

Role:
- Used by `TestNVMe.setup_log_dir` to capture per-test stdout/stderr while still printing to the terminal/TAP diagnostic stream.
