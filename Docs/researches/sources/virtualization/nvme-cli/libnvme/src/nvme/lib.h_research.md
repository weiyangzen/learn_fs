# File Research: sources/virtualization/nvme-cli/libnvme/src/nvme/lib.h

Public libnvme core API declarations.

Key API areas:
- Global context lifecycle:
  - `libnvme_create_global_ctx()`
  - `libnvme_free_global_ctx()`
- Logging:
  - log levels
  - default log level
  - set/get logging level, PID flag, timestamp flag
- Transport handles:
  - open/close
  - get fd/name/MI endpoint
  - test whether handle is controller, namespace, direct, or MI
- Passthrough hooks:
  - submit-entry callback
  - submit-exit callback
  - retry-decision callback
  - default timeout setter
- Global behavior toggles:
  - MI endpoint probing
  - dry run
  - ioctl probing

Research notes:
- The header describes Linux naming semantics for `libnvme_open()`, while implementation also supports `mctp:` and test-handle names.
- Hook callbacks are part of the public API, enabling tracing, custom retry logic, and per-command state management without modifying submission code.
