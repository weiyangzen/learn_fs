# sources/test-tools/unionmount-testsuite/tests/open-plain.py

Purpose: baseline tests for opening existing regular files without create/truncate/exclusive flags.

Important APIs/types/functions: five `subtest_*` functions using `ctx.open_file`.

Control flow: read-only opens verify original content twice. Write-only/read-write overwrites first byte from `q` to `p`. Append modes append `q` and `p`. Readbacks after each mutation validate expected content.

State and persistence: write-like operations copy up lower data to upper and mutate it; read-only operations should not.

Dependencies and integration: lower regular files created by setup and context content/layer validation.

Risks: repeated mutations mean each subtest assumes a fresh setup context from the runner.

Test signals: foundational regular-file open, write, append, and copy-up coverage.
