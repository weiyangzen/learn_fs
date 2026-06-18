# File Research: sources/os/linux/linux-stable/fs/pstore/ftrace.c

## Summary
Implements persistent function tracing into pstore. It registers an ftrace callback that writes compact call records to the active pstore backend and provides a debugfs knob to enable or disable recording.

## Main Responsibilities
- Capture function IP, parent IP, timestamp, and CPU into `struct pstore_ftrace_record`.
- Adjust and decode IPs when KASLR is active and persistent addresses need normalization.
- Register/unregister ftrace ops based on module parameter or debugfs writes.
- Create `/sys/kernel/debug/pstore/record_ftrace`.
- Merge multiple ftrace logs in timestamp order when reading recovered records.

## Key Interfaces
- `pstore_register_ftrace()` sets up debugfs and optionally starts ftrace recording.
- `pstore_unregister_ftrace()` disables recording and removes debugfs entries.
- `decode_ip()` is used by pstorefs display code to recover original symbols.
- `pstore_ftrace_combine_log()` merges two binary ftrace record streams.

## Important Behavior
The ftrace callback runs `notrace`, avoids recursion with `ftrace_test_recursion_trylock()`, disables local IRQs, and writes directly through `psinfo->write()`. It skips recording while `oops_in_progress` is set.

The timestamp counter intentionally is not atomic; the comment states that speed is preferred over exact ordering. Merge logic sorts by record timestamp and drops any leading partial record bytes by aligning sizes to `sizeof(struct pstore_ftrace_record)`.

## State and Synchronization
`pstore_ftrace_lock` serializes enable/disable operations. `record_ftrace` is both a module parameter and runtime state. `pstore_ftrace_stamp` is a global monotonically increasing best-effort counter.

## Cross-File Interactions
`inode.c` formats ftrace records through seq_file using `decode_ip()`. `ram.c` and `zone.c` call `pstore_ftrace_combine_log()` to merge per-CPU or per-zone logs.

## Risks
Ftrace persistence writes from sensitive contexts and depends on backend write behavior. Timestamp ordering is approximate because the stamp counter is not atomic.
