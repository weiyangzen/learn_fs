# sources/sync-backup/rsync/testsuite/cvs-exclude_test.py

Purpose: depth coverage for `-C`/`--cvs-exclude`, including built-in CVS cruft patterns and scoped `.cvsignore`.

Important APIs/types/functions: `makepath`, `run_rsync('-aC')`, `assert_exists`, and `assert_not_exists`.

Control flow: create a four-level tree containing real `.c` files plus built-in cruft (`*.o`, `*~`) at each level. Add `.cvsignore` under `d1/d2` for `*.junk`, create both a scoped junk file and a top-level junk file, sync with `-C`, and verify only intended files are excluded.

State and persistence behavior: destination tree should contain real files and top-level junk while excluding built-in cruft and deep scoped junk.

Dependencies and integration points: rsync filter engine, CVS exclude defaults, per-directory `.cvsignore` scope.

Risks and test signals: failures identify incorrect built-in pattern handling or `.cvsignore` scope leakage.
