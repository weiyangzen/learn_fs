<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/_newselect-P.c -->
## sources/test-tools/strace/tests/_newselect-P.c

Purpose: Thin compile-time variant of the `_newselect` decoder test that enables path/file-descriptor tracing behavior for fd 9.

Important APIs/types/functions: Defines `PATH_TRACING_FD 9` and includes `_newselect.c`.

Control flow: There is no local runtime logic; compilation flows directly into `_newselect.c`, which then includes the generic `xselect.c` test body with the fd-tracing macro visible.

State and persistence: No state of its own.

Dependencies and integration: Built as `_newselect-P` by `Makefile.am`; depends entirely on `_newselect.c` and `xselect.c` respecting `PATH_TRACING_FD`.

Risks: As a wrapper, its correctness is easy to break by renaming macros or changing `xselect.c` expectations without updating this file.

Test signals: The resulting executable should produce the same `_newselect` coverage as `_newselect.c` plus fd/path tracing expectations for descriptor 9.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/_newselect-P.c -->
