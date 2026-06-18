# sources/test-tools/unionmount-testsuite/tests/noent-creat.py

Purpose: tests ordinary `O_CREAT` behavior for previously missing files.

Important APIs/types/functions: five `subtest_*` functions using `ctx.open_file`.

Control flow: read-only create makes an empty file. Write-only/read-write creates and overwrites first byte from `q` to `p`. Append creates with `q` then appends `p`, producing `qp`. Readbacks confirm each state.

State and persistence: creates upper files and mutates content through normal write/append semantics.

Dependencies and integration: uses setup missing path records, context open creation, write, and read validation.

Risks: terminal slash mode can force creation errors; append semantics assume file offset behavior from `O_APPEND`.

Test signals: baseline creation coverage for missing regular files.
