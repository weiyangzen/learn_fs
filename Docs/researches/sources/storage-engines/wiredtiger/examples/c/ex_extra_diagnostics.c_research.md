# sources/storage-engines/wiredtiger/examples/c/ex_extra_diagnostics.c

Purpose: demonstrates enabling and updating WiredTiger extra diagnostic checks at runtime.

Important APIs and control flow: `main` obtains WT_HOME and then branches on `HAVE_DIAGNOSTIC`. In diagnostic builds, diagnostics are always enabled, and configuring `extra_diagnostics=[key_out_of_order]` is asserted to return `EINVAL`. In non-diagnostic builds, it opens with `extra_diagnostics=[key_out_of_order]` and then reconfigures the connection to `extra_diagnostics=[txn_visibility]`, implicitly disabling omitted diagnostics.

State and persistence: opens a connection and mutates runtime connection diagnostic configuration. No explicit table state is created.

Dependencies and integration: depends on build-time `HAVE_DIAGNOSTIC`, WiredTiger connection configuration, `conn->reconfigure`, and `test_util.h`.

Risks: the non-diagnostic branch does not close the connection before returning, so it relies on process cleanup. Diagnostic options are version/configuration sensitive, so example expectations must track supported option names and diagnostic-mode semantics.

Test signals: diagnostic builds must observe `EINVAL`; non-diagnostic builds must open and reconfigure successfully.
