# sources/test-tools/fio/libfio.c

Purpose: central fio library initialization, teardown, runstate utilities, termination signaling, IO counter resets, and environment/architecture metadata.

Important APIs/functions: `clear_io_state`, `reset_all_stats`, `reset_fio_state`, `fio_get_os_string`, `fio_get_arch_string`, `runstate_to_name`, `td_set_runstate`, `td_bump_runstate`, `td_restore_runstate`, `fio_mark_td_terminate`, `fio_terminate_threads`, `fio_running_or_pending_io_threads`, `fio_set_fd_nonblocking`, `initialize_fio`, and `deinitialize_fio`.

Control flow: initialization performs compile-time layout assertions, runtime endian validation, architecture init, smalloc init, file lock and file hash init, locale setup, page-size discovery, and keyword initialization. Reset paths zero counters, close/reposition files, reseed random generators when requested, clear inflight IO, reset runtime/stat timestamps, and helper state. Termination iterates thread data and either marks terminate, sends SIGTERM, or calls engine terminate hooks depending on state.

State/persistence: owns global `disk_list`, `arch_flags`, `page_mask`, and `page_size`; mutates thread/job globals such as group and segment counters; updates `thread_data` runstate and termination fields.

Dependencies/integration: includes core fio headers, OS/arch layers, file locks, helper threads, file hashes, locale, signals, and fcntl. It is an integration hub for almost every fio subsystem.

Risks/test signals: endian/config mismatch aborts initialization; runstate transitions are not independently synchronized here; termination behavior depends on process/thread model and IO engine hooks. Tests should cover initialization failure paths, page-size setup, runstate naming assertions, and reset behavior across time-based/verify jobs.
