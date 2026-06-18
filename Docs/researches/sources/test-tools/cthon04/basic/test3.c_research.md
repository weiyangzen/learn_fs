# sources/test-tools/cthon04/basic/test3.c

Purpose: repeated lookup/getcwd/stat test intended to exercise directory lookup across the mounted test point.

Important APIs/types/functions: parses -h, -t, -f, -n plus count. Uses getcwd(), stat(), testdir()/mtestdir(), timing helpers, and complete().

Control flow: enters or reuses the test directory, optionally starts a timer, then loops count times calling getcwd() into MAXPATHLEN storage and stat() on the returned path.

State and persistence: aside from optional test-directory creation, the loop is read-only and leaves no files behind.

Dependencies and integration points: depends on tests.h for MAXPATHLEN and default TESTDIR; compiled with Unix headers or DOS/Win32 time compatibility.

Risks: assumes getcwd output fits MAXPATHLEN; -n requires an existing directory; failures are fatal at first missing cwd/stat.

Test signals: prints total getcwd/stat calls and optional elapsed time before complete().
