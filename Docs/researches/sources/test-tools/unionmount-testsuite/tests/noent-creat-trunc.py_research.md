# sources/test-tools/unionmount-testsuite/tests/noent-creat-trunc.py

Purpose: verifies missing-file creation with `O_CREAT|O_TRUNC`, including repeated truncation and append behavior.

Important APIs/types/functions: five `subtest_*` functions using `ctx.open_file`.

Control flow: first open creates the file. Repeated read-only create/truncate keeps it empty; write and read-write overwrite content from `q` to `p`; append mode appends `p` to existing `q` when the second open omits truncate in those subtests.

State and persistence: creates and mutates upper files with expected content transitions.

Dependencies and integration: exercises open/create/truncate/data-copy-up state in `context.py`.

Risks: append plus truncate sequencing is easy to misread; context expectations encode exact contents.

Test signals: validates creation/truncation data semantics on upper files.
