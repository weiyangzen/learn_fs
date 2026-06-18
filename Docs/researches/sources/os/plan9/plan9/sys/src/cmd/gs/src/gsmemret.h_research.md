# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gsmemret.h

Declares the retrying allocator wrapper. Defines `gs_memory_recover_status_t` with `RECOVER_STATUS_NO_RETRY` and `RECOVER_STATUS_RETRY_OK`, plus the recovery callback signature.

`gs_memory_retrying_t` embeds `gs_memory_common`, target allocator, recovery procedure, and recovery data. Exports init/release, recovery-closure setter, and target accessor. Like the locked wrapper, it does not track target data itself.
