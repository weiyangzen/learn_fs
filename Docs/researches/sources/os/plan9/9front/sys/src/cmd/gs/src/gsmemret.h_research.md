# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gsmemret.h

Interface for retrying memory allocator wrapper.

Key definitions:
- `gs_memory_retrying_t` embeds `gs_memory_common`, target allocator, recovery proc, and recovery proc data.
- `gs_memory_recover_status_t`: `RECOVER_STATUS_NO_RETRY` or `RECOVER_STATUS_RETRY_OK`.
- `gs_memory_recover_proc_t` callback signature.

Key declarations:
- `gs_memory_retrying_init`
- `gs_memory_retrying_release`
- `gs_memory_retrying_set_recover`
- `gs_memory_retrying_target`

Research notes:
- Comments clarify that this wrapper does not track acquired memory, so `free_all` with `FREE_ALL_DATA` is a no-op at wrapper level.
