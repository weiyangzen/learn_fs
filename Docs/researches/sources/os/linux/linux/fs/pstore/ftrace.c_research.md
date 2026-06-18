# File Research: sources/os/linux/linux/fs/pstore/ftrace.c

## Role

Provides the persistent ftrace frontend for pstore. It records function trace records into the active pstore backend and exposes a debugfs knob to enable or disable recording.

## Key Functions

- `pstore_ftrace_call()` is the ftrace callback. It avoids oops recursion, disables local IRQs, encodes IP, parent IP, timestamp, and CPU, then calls `psinfo->write()` with `PSTORE_TYPE_FTRACE`.
- `adjust_ip()` and `decode_ip()` compensate for KASLR when pstore is built in and `PSTORE_CPU_IN_IP` is not used.
- `pstore_set_ftrace_enabled()` registers or unregisters the ftrace ops and updates `record_ftrace`.
- `pstore_register_ftrace()` creates `debugfs/pstore/record_ftrace` and enables initial recording if requested.
- `pstore_unregister_ftrace()` disables tracing and removes debugfs entries.
- `pstore_ftrace_combine_log()` merges two buffers of `pstore_ftrace_record` entries by timestamp.

## Research Notes

The implementation prioritizes trace-path simplicity and low overhead. The timestamp counter is deliberately not atomic: ordering is useful but exactness is less important than avoiding heavy synchronization in ftrace paths.
