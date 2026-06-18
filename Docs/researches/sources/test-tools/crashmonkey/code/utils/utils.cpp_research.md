# sources/test-tools/crashmonkey/code/utils/utils.cpp

Purpose: implements disk-write utility types used to represent block IO log entries and crash-state data fragments. It provides flag classification, binary serialization, deserialization, formatting, and data ownership helpers.

Important APIs/types/functions: `disk_write` constructors, `is_async_write`, `is_barrier`, `is_meta`, `is_checkpoint`, equality operators, `serialize`, `deserialize`, `flags_to_string`, flag setters/clearers, `set_data`, `get_data`, `clear_data`, `DiskWriteData`, and `GetData`. It depends on `disk_wrapper_ioctl.h` flag definitions.

Control flow: serialization writes a 4 KiB metadata block in big-endian fields followed by zero-padded 4 KiB data blocks. Deserialization reads the same blocks, reconstructs metadata, allocates data, and returns a `disk_write`. Flag helpers test HWM bits for write, flush, FUA, soft barrier, metadata, and checkpoint semantics.

State/persistence behavior: serializes kernel-observed writes into log files and provides pointers into shared data for replay. `DiskWriteData` avoids copies by retaining a shared base pointer and offset.

Dependencies/integration: used by permuters, tests, and harness snapshot/replay code. Risks/test signals: deserialization uses asserts rather than recoverable errors, allocates even for zero-sized data, and binary streams are opened without explicit `ios::binary` in tests on POSIX.
