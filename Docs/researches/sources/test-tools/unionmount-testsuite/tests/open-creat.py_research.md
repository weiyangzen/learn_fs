# sources/test-tools/unionmount-testsuite/tests/open-creat.py

Purpose: tests `O_CREAT` on existing lower files without truncation.

Important APIs/types/functions: five `subtest_*` functions using `ctx.open_file`.

Control flow: read-only create reads original content. Write-only/read-write writes `q` then `p` at the start, preserving the rest of the file. Append variants append `q` then `p`, producing original content plus suffixes.

State and persistence: write-like opens copy data up and mutate content in upper layer; read-only does not.

Dependencies and integration: context open/write/read and lower regular fixture content.

Risks: assumes write starts at offset zero when not append; terminal slash can change error handling.

Test signals: validates create-as-open semantics and data preservation on existing files.
