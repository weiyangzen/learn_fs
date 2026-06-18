# sources/distributed-fs/tahoe-lafs/src/allmydata/test/cli/test_cp.py

## Purpose
This module is the detailed behavior suite for `tahoe cp`. It validates local-to-grid, grid-to-local, grid-to-grid, filecap/dircap, recursive, Unicode, mutable overwrite, read-only mutable, verbose output, trailing slash, destination naming, duplicate directory, empty directory, and collision behavior.

## Important APIs, Types, and Functions
- `Cp` is the main command behavior test case using `GridTestMixin` and `CLITestMixin`.
- `CopyOut` is a table-driven test case for copying Tahoe objects out to the local filesystem.
- `COPYOUT_TESTCASES` encodes dozens of `cp`/`cp -r` scenarios with expected filesystem results or normalized error codes.
- `CopyOut.do_setup` builds a Tahoe hierarchy containing parent dircaps, child dircaps, filecaps, alias mappings, empty directories, and colliding directory names.
- `CopyOut.run_one_case`, `do_one_test`, and `do_tests` substitute caps into table rows, reset the local target tree, run the CLI, normalize stderr into symbolic errors, and compare observed output trees.

## Control Flow
The `Cp` class starts with simple parser and Unicode filename checks, then builds increasingly complex grids. Tests create aliases, upload files, call `cp`, use `get` or `ls --json` to inspect results, and assert both content and capability stability. Mutable tests capture original read-write/read-only URIs, copy new local data over existing mutable nodes, and verify in-place updates retain mutable URIs while immutable replacements produce new caps. The copy-out matrix creates a known Tahoe filesystem once, then iterates every scenario from the table, resetting the local destination for each row.

## State and Persistence Behavior
The tests create local source files, symlinks, output directories, target files, and full directory trees under test basedirs. Remote state includes aliases, mutable files, immutable files, literal filecaps, directory caps, nested directories, empty directories, and read-only links. `CopyOut.check_output` walks the local target tree and encodes both directory presence and file contents into a set for comparison. The read-only mutable tests intentionally preserve server state after failed overwrites to confirm no partial update occurred.

## Dependencies and Integration Points
The module depends on `cli.CpOptions`, Twisted `defer`, Tahoe `fileutil`, encoding helpers `quote_output`, `unicode_to_output`, `to_bytes`, `GridTestMixin`, `CLITestMixin`, and `skip_if_cannot_represent_filename`. It integrates with other CLI commands (`create-alias`, `put`, `mkdir`, `ln`, `ls`, `get`) as setup and verification tools, so it covers the copy command through realistic command-line workflows rather than isolated internals.

## Risks and Edge Cases
Covered risks include Unicode conversion failures, dangling symlink recursion assertions, unnamed caps copied into directories, target slash semantics, collisions from multiple source trees, directory-to-file errors, recursive copy requirements, duplicate origin/destination directories, mutable file content replacement, and read-only mutable overwrite refusal. The table-driven expectations are central because small path parsing changes can silently alter copy semantics.

## Test Signals
The strongest signal is the table-driven `CopyOut` matrix, which turns complex path/cap combinations into deterministic expected local trees or exact error classes. Additional high-value signals are content round-trips, JSON cap comparison, URI retention checks for mutable nodes, and exact verbose progress output. A residual risk is the large Deferred chains can obscure the failing step unless Trial reports callback context clearly.
