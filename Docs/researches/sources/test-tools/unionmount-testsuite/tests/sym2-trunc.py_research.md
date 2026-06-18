# sources/test-tools/unionmount-testsuite/tests/sym2-trunc.py

Purpose: verifies truncating opens through an indirect symlink chain to an existing file.

Important APIs and functions: five subtests combine `ctx.indirect_sym()` with `ctx.open_file(..., tr=1)` and mode flags.

Control flow: each case opens through the indirect symlink with truncation. Read-only checks an empty target; write modes write one byte after truncation and verify the target contains only that byte.

State and persistence: target data is truncated through a two-hop link path. The symlink objects should not be replaced or truncated.

Dependencies and integration: depends on the context's indirect symlink fixtures and open flag mapping. Exercises overlay copy-up and truncation of lower target data.

Risks: platform behavior for `O_TRUNC|O_RDONLY` can differ outside the intended Linux environment.

Test signals: empty or single-byte target reads after truncating opens.
