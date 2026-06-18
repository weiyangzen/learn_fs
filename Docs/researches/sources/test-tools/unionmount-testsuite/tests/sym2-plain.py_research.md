# sources/test-tools/unionmount-testsuite/tests/sym2-plain.py

Purpose: tests ordinary open/read/write/append behavior through an indirect symlink chain.

Important APIs and functions: five `subtest_*` functions use `ctx.indirect_sym()` and `ctx.open_file()` with `ro`, `wo`, `rw`, and `app` flag combinations.

Control flow: the file is read through the chain, then overwritten or appended twice depending on subtest. Each mutation is verified by a read through the same indirect path.

State and persistence: persistent data changes only at the ultimate target; symlink dentries should remain unchanged.

Dependencies and integration: relies on unionmount context fixture isolation and Linux symlink-following semantics through overlay layers.

Risks: multi-hop symlink resolution can expose path normalization or copy-up bugs that direct-symlink tests do not catch.

Test signals: expected contents after each operation and no unexpected open failures.
