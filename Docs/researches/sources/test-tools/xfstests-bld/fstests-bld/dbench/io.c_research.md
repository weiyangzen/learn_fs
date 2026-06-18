<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests-bld/fstests-bld/dbench/io.c -->
# sources/test-tools/xfstests-bld/fstests-bld/dbench/io.c

Source read: complete file, 209 lines, 4359 bytes, sha256 `0b92196b7a80cd75a0b63cd1cbbead832b387b5e03df12e9a6e4cce46d41b593`. Final split target: `Docs/researches/sources/test-tools/xfstests-bld/fstests-bld/dbench/io.c_research.md`.

Purpose: older direct syscall wrapper layer for simple file-operation trace replay. It maintains a process-global open-file table and exposes `do_*` helpers for create/open/read/write/stat/close/unlink/mkdir/rmdir/rename.

Important APIs/types/functions: `ftable[MAX_FILES]` maps integer trace handles to fds; static `buf[70000]` provides shared read/write data; `do_open()` creates/truncates/expands files and records handles; `expand_file()` writes zeroed chunks; `do_write()` and `do_read()` seek then transfer; `do_stat()` checks file size; `do_create()` opens and closes a fixed temporary handle.

Control flow: callers pass mutable path strings, which are uppercased by `strupper()` before filesystem operations. `do_open()` creates the file, adjusts size to match trace expectations, inserts the handle into the first empty table slot, and prints progress every hundred opens. Read/write/close search the global table linearly and return with diagnostics if the handle is absent.

State and persistence behavior: modifies files/directories in the current working tree, persists created file sizes, and keeps open descriptor mappings in static process state. It uses external `line_count` only for diagnostics and does not maintain per-child state.

Dependencies and integration: includes `dbench.h` for POSIX headers, `MIN`, and prototypes. It relies on `strupper()` from another dbench source file not in this item and on `line_count` from the trace parser. This layer appears to coexist with newer `nb_*` replay code but is a simpler API family.

Risks: fixed 1000-entry handle table, ignored short reads, partial error handling, no bounds check when `do_write()` writes `size` bytes from a 70000-byte buffer, and path mutation via `strupper()` can surprise callers. The global table is not thread-safe and is unsuitable for multi-client sharing without process isolation.

Test signals: simple trace tests should check case transformation, open/expand/truncate behavior, handle-missing diagnostics, file size validation, and cleanup after mkdir/rmdir/rename/unlink operations.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests-bld/fstests-bld/dbench/io.c -->
