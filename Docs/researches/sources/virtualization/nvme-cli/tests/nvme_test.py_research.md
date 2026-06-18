# File Research: sources/virtualization/nvme-cli/tests/nvme_test.py

Shared base class and utility library for nvme-cli Python integration tests.

Key elements:
- Loads `config.json` for controller, namespace, log directory, optional binary path, PCI validation flag, and log level.
- Validates the configured controller is PCI-backed by searching `/sys/devices`.
- Detects namespace management/attachment support from Identify Controller OACS bits.
- If namespace management is supported, recreates and attaches default namespace 1 in setup and teardown.
- Provides robust JSON parsing helpers with typed assertions.
- Wraps command execution through `subprocess.run(shell=True)` with logging.
- Provides helpers for reset, controller ID, namespace list, max namespace count, LBA status support, active LBA format, DPS/PIF, metadata extension, LBA format size, NVM capacity, identify field extraction, copy format support, namespace create/attach/detach/delete, SMART/error logs, and simple namespace I/O.

Important behavior:
- The base setup can delete all namespaces when namespace management is supported.
- `run_ns_io` uses `dd` reads and zero writes against the namespace block device.
- `setup_log_dir` redirects stdout/stderr to `TestNVMeLogger`.

Role:
- Central fixture for all hardware-backed Python tests.
