<!-- BEGIN_FILE_RESEARCH: sources/test-tools/kdevops/scripts/generate_refs.py -->
# sources/test-tools/kdevops/scripts/generate_refs.py

Purpose: generates Kconfig choices for git references or kernel.org release references. It supports remote `git ls-remote` refs and `kernel.org/releases.json`, optional static extra configs from YAML, and daily regeneration throttling.

Important APIs and functions: `popen()` runs subprocesses and returns stdout; `parser()` defines shared options and `gitref`/`kreleases` subcommands; `check_file_date()` skips fresh outputs unless `--force`; `_ref_generator_choices_static()` and `_ref_generator_choices()` emit Kconfig symbols; `ref_generator()` writes the final Kconfig file; `remote()` runs `git ls-remote`; `gitref_getreflist()` extracts ref names; `_get_extraconfs()` loads YAML; `_check_connection()` probes network; `gitref()` and `kreleases()` gather refs; `main()` dispatches.

Control flow: parse known args, skip fresh output unless forced, dispatch to the selected subcommand, gather dynamic and static refs, then rewrite the output Kconfig file from scratch.

State and persistence: creates parent directories, removes existing output, and writes generated Kconfig. Network availability gates dynamic generation for both git and kernel.org paths.

Dependencies and integration: git, PyYAML, urllib, socket, and Kconfig generator Makefiles (`gen-refs-*`). It feeds boot/kernel reference menu choices.

Risks: `popen()` references `stdout` even when `comm=False`, which would be undefined if used that way. Network probe host is hardcoded to kernel.org for all gitref repos. If connection fails, `gitref()` emits no file. YAML schema is assumed. Test signals include fixture YAML, mocked subprocess output, forced/fresh-date behavior, kernel release JSON fixtures, and no-network behavior.
<!-- END_FILE_RESEARCH: sources/test-tools/kdevops/scripts/generate_refs.py -->
