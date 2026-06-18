# sources/test-tools/xfstests-bld/fstests-bld/e2fsprogs-libs/lib/ss/test_ss.c

## Purpose
`test_ss.c` is the regression and demonstration program for libss.

## Important APIs, Types, and Functions
It uses generated `test_cmds`, standard `ss_std_requests`, `ss_create_invocation()`, `ss_add_request_table()`, `ss_execute_line()`, `ss_listen()`, and defines the sample handler `test_cmd()`.

## Control Flow
`main()` parses `-R` and `-f`, creates an invocation named `test_ss`, adds standard requests after test commands, prints a banner, then executes one request, sources a command file, or enters interactive listening. `source_file()` reads commands, skips comments, optionally suppresses echo for lines prefixed by `-`, executes each line, and counts failures.

## State, Persistence, Dependencies, Risks, and Test Signals
State is the invocation and test script input. Dependencies include generated command table from `test_cmd.ct` and libss/libcom_err. Risks include limited option handling, fixed 256-byte command buffer, and output text coupling to expected files. Test signals are `make check` diffing `test_out` against `test_script_expected`.
