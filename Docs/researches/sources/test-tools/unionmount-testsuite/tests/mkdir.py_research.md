# sources/test-tools/unionmount-testsuite/tests/mkdir.py

Purpose: tests directory creation over missing names, existing files/dirs, symlink paths, populated parents, and dangling symlinks.

Important APIs/types/functions: eleven `subtest_*` functions using `ctx.mkdir`, `ctx.open_file`, and symlink/path helpers.

Control flow: creates a new missing directory then rejects duplicate creation, rejects mkdir over files and existing dirs with `EEXIST`, creates subdirectories inside empty and populated lower dirs, rejects mkdir over direct/indirect symlinks to files or dirs, and rejects over dangling symlink paths. Follow-up opens confirm existing targets remain.

State and persistence: successful mkdir creates upper directories and may trigger remount/upper rotation in recycle mode. Failed operations mark failed creates but should not alter existing fixtures.

Dependencies and integration: exercises `context.mkdir`, terminal slash handling, symlink pathwalk, and remount-on-create behavior.

Risks: mkdir over symlink errno depends on terminal slash and follow semantics; recycled layer checks depend on overlay feature flags.

Test signals: coverage for directory creation/copy-up across lower and upper parents.
