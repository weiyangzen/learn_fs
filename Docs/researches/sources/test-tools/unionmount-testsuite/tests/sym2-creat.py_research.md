# sources/test-tools/unionmount-testsuite/tests/sym2-creat.py

Purpose: validates `O_CREAT` opens through an indirect symlink chain to an existing file.

Important APIs and functions: five subtests use `ctx.indirect_sym()` and `ctx.open_file()` in read-only, write-only, append, and read/write forms.

Control flow: read-only creates are no-ops over an existing target. Other cases write `q` and then `p`, either overwriting the first byte or appending at end, then verify content.

State and persistence: target content changes through a two-hop symlink path; the symlink chain should remain intact.

Dependencies and integration: depends on correct resolution of indirect symlink fixtures and copy-up behavior for lower targets modified through links.

Risks: because `direct` and `f` variables are assigned but unused, the test relies entirely on fixture names being created by context helpers rather than local checks.

Test signals: readbacks through the indirect symlink show exact overwrite or append content.
