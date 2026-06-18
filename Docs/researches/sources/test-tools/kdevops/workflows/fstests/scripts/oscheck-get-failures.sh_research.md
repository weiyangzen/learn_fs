## sources/test-tools/kdevops/workflows/fstests/scripts/oscheck-get-failures.sh

Purpose: Prints the unique list of known failure test IDs for the current OS, filesystem, and section by reusing oscheck expunge resolution.

Important APIs/types/functions: Uses `oscheck-lib.sh` functions: `oscheck_lib_init_vars`, `oscheck_lib_set_run_section`, `oscheck_lib_get_host_options_vars`, `oscheck_lib_read_osfiles_verify_kernel`, `oscheck_lib_validate_section`, `oscheck_lib_set_expunges`, and `oscheck_lib_mktemp`.

Control flow: Parses `--test-section`, initializes oscheck with non-failure expunges skipped and quiet distro checks, resolves section and expunge files, concatenates the first field from every expunge file, sorts, uniques, and prints non-empty IDs.

State and persistence: Creates a temporary file through `oscheck_lib_mktemp` and removes it. It otherwise reads configs and expunge files only.

Dependencies and integration points: Requires `FSTYP`, host config, os-release data, expunge file tree, and oscheck library. Intended for automation that needs the known-failure list rather than running tests.

Risks and test signals: It intentionally skips non-failure expunges, so output differs from the full `oscheck.sh` exclude set. Test by comparing with `oscheck.sh -n --expunge-list` and confirming only known failures appear.
