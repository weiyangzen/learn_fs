# File Research: sources/virtualization/spdk/lib/accel/accel_internal.h

`accel_internal.h` is the private header shared by accel core, RPC, and software-module code. It includes public accel/module headers, queue utilities, and config state.

It defines `ACCEL_AES_XTS`, the internal `module_info` structure used to report a module name and supported opcodes, `accel_operation_stats`, and `accel_stats`. The stats structure mirrors what the RPC layer exposes: per-op executed/failed/bytes, sequence counts, outstanding counts, and retry counters.

The header declares `_accel_for_each_module()`, crypto string conversion helpers, JSON dump helpers for crypto-key parameters and key lists, and `accel_get_stats()`. These are intentionally internal and support the RPC/control-plane files without exposing implementation details through public headers.

Research notes: this file is small but forms the internal ABI between `accel.c` and `accel_rpc.c`; changes to `accel_stats` or crypto dump helpers must be kept in sync with the RPC response shape.
