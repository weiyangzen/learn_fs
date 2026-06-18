# sources/test-tools/fs-mark/fs_mark.h

Purpose: shared constants, global configuration/state, structs, strings, buffer storage, and timing prototypes for `fs_mark.c`.

Important APIs/types: defines maximums (`MAX_IO_BUFFER_SIZE`, `MAX_FILES`, `MAX_THREADS`, path/name/string sizes), defaults, directory policies, sync policy bits and composite methods, global runtime options (`io_buffer_size`, `file_size`, `num_files`, subdir settings, sync method, logging, loop/file counts), static IO/name buffers, `struct name_entry`, `child_job_t`, and `fs_mark_stat_t`. Declares timing helpers `start()`, `stop()`, and `tvnow()`.

Control flow/state: because this header defines globals rather than declaring externs, it is intended for a small program with one main translation unit including it. Policy string arrays are also defined here and used by reporting.

Dependencies/integration: relies on `PATH_MAX` and `FILE` being available before inclusion via `fs_mark.c` includes. `lib_timing.c` supplies timing functions.

Risks/test signals: defining globals in a header would create multiple-definition problems if included by more than one linked source. Fixed-size buffers drive many fs_mark path risks. Compile/link tests should ensure only `fs_mark.c` includes it as a definition header.
