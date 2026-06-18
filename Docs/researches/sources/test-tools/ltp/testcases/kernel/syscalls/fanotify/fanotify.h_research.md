# sources/test-tools/ltp/testcases/kernel/syscalls/fanotify/fanotify.h

Purpose: Shared fanotify test helper header wrapping initialization, mark operations, feature probing, file-handle capture, and event-info parsing.

Important APIs/types/functions: `SAFE_FANOTIFY_INIT`, `SAFE_FANOTIFY_MARK`, `fanotify_get_fid`, `fanotify_save_fid`, `fanotify_flags_supported_on_fs`, `fanotify_get_supported_init_flags`, `get_event_info_*`, and many `REQUIRE_*` macros.

Control flow: Wrappers convert `ENOSYS`/unsupported flag combinations into `TCONF` and unexpected syscall errors into `TBROK`. FID helpers collect `statfs` fsid plus `name_to_handle_at` handles. Support probes open temporary fanotify groups and optionally try marks on a path.

State and persistence behavior: No global state is stored, but helper calls inspect kernel/filesystem support and may create short-lived fanotify fds and marks.

Dependencies and integration points: Included by all fanotify tests when `HAVE_SYS_FANOTIFY_H` is available; it integrates LTP safe macros with Linux fanotify and file-handle APIs.

Risks and test signals: Because the header centralizes support detection, incorrect errno classification can skip or break many tests. The known-flags mask must be updated when new fanotify init flags are added.
