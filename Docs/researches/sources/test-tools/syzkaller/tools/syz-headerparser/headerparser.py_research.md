# sources/test-tools/syzkaller/tools/syz-headerparser/headerparser.py

Purpose: command-line entry point for the legacy header parser that emits syzkaller struct metadata from C headers.

Important APIs and flow: `main` parses `--filenames`, `--debug`, and optional `--include`. It chooses logging level, reads include-line content when provided, constructs `GlobalHierarchy` from comma-separated filenames, handles preprocessing errors by logging the final traceback line and exiting `-1`, and prints `gh.get_metadata_structs()`.

State and persistence: reads input headers and optional include file; writes only stdout/stderr.

Dependencies and integration: depends on `headerlib.container.GlobalHierarchy` and `HeaderFilePreprocessorException`. It is a standalone helper around the Python headerlib stack.

Risks: comma-separated filenames cannot represent filenames containing commas. Missing include files are not caught separately. Error reporting intentionally truncates traceback detail.

Test signals: expected output for `test_headers/th_a.h,th_b.h` is the main manual/legacy regression path.
