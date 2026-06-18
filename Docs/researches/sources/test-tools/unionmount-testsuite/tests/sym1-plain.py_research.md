# sources/test-tools/unionmount-testsuite/tests/sym1-plain.py

Purpose: validates plain opens through a direct symlink to an existing file without create or truncate flags.

Important APIs and functions: five subtests call `ctx.open_file()` on `ctx.direct_sym()` with read-only, write-only, append write-only, read/write, and append read/write modes.

Control flow: read-only subtests verify baseline content. Write modes overwrite first bytes, while append modes append `q` then `p`, and each mutation is followed by a read check.

State and persistence: target file data persists across operations within each subtest. The symlink object should remain a symlink; only the target content changes.

Dependencies and integration: depends on harness fixtures and open flag conversion. It exercises symlink resolution through the union filesystem.

Risks: shared fixture reuse across subtests could be problematic if the harness does not reset state; these tests assume isolated subtest setup.

Test signals: expected content after overwrite or append, with no unexpected creation or symlink replacement.
