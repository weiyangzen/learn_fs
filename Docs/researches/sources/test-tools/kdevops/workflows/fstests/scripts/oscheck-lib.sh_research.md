## sources/test-tools/kdevops/workflows/fstests/scripts/oscheck-lib.sh

Purpose: Shared library for fstests OS-aware test preparation, section parsing, distro detection, expunge-file discovery, and validation.

Important APIs/types/functions: Major functions include `oscheck_lib_init_vars`, `known_hosts`, `oscheck_lib_set_run_section`, `oscheck_lib_parse_config_section`, `oscheck_include_os_files`, `oscheck_add_expunge_if_exists`, `oscheck_handle_section_expunges`, `oscheck_read_osfile_and_includes`, `oscheck_distro_kernel_check`, `oscheck_lib_validate_section`, and `oscheck_lib_set_expunges`.

Control flow: Initialization validates `FSTYP`, sets default paths, release variables, kernel version, and expunge controls. Runtime helpers infer the test section, parse host config sections with `sed`/`eval`, load OS-specific helpers based on os-release ID, run distro-kernel checks, assemble expunge candidates by category/priority/section, add quick-test and large-disk excludes, and validate that intended section expunges were queued.

State and persistence: Maintains state through exported shell variables such as `OSCHECK_ID`, `VERSION_ID`, `RUN_SECTION`, `EXPUNGE_FLAGS`, `EXPUNGE_FILES`, `OSCHECK_EXCLUDE_DIR`, and `KERNEL_VERSION`. It writes only temporary files when callers request `oscheck_lib_mktemp`.

Dependencies and integration points: Sourced by `oscheck.sh` and `oscheck-get-failures.sh`. Depends on host config files, `/etc/os-release`, distro helper files under `osfiles`, expunge file layout, `lsb_release`, and `/boot` kernel metadata for distro-specific checks.

Risks and test signals: Section parsing uses `eval` on config content, so config files must be trusted. A likely bug in `oscheck_lib_set_run_section` assigns `RUN_SECTION="${FSTYP}_${s}"` even though `s` is not defined; this affects short section names without filesystem prefixes. Test with full and short section names, `--expunge-list`, distro-kernel checks, and missing-expunge verification.
