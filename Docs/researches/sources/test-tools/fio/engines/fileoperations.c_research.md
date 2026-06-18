# sources/test-tools/fio/engines/fileoperations.c

Purpose: Implements six metadata-only engines: `filecreate`, `filestat`, `filedelete`, `dircreate`, `dirstat`, and `dirdelete`, measuring create/stat/delete latency without normal data IO.

Important APIs/functions: Shared `fc_data` records operation type and latency direction. Options for stat engines choose `stat`, `lstat`, or `statx`. Helpers include `setup_dirs()`, `open_file()`, `stat_file()`, `delete_file()`, `queue_io()`, `get_file_size()`, `init()`, `cleanup()`, and `remove_dir()`.

Control flow: Init infers file versus directory operation from the engine name and selects read/write latency bucket. Directory stat/delete setup creates target directories first. The open callback is repurposed as the measured operation: create engines create a file or directory, stat engines perform the configured stat call, and delete engines unlink/rmdir. Each measured path records completion latency via `add_clat_sample()` unless latency is disabled. Queue only handles sync operations and otherwise completes immediately.

State/persistence: Per-thread `fc_data` is allocated in init and freed in cleanup. Files/directories are created or removed on disk according to engine semantics.

Dependencies/integration: Uses POSIX file APIs, fio statx wrapper, latency sampling, generic close, and engine registration.

Risks: `fio_mkdir(f->file_name, S_IFDIR)` in `open_file()` for directory create is unusual because mode bits normally use permissions. `statx` path uses `realpath()`, so it fails for missing paths rather than measuring negative lookup. `init()` does not check `calloc()` failure.

Test signals: Run each engine with multiple files, latency enabled/disabled, all stat types, preexisting directories, delete of missing files, and sync directions.
