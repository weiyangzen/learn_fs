<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/s3fs-fuse/Makefile.am -->
# sources/user-network-fs/s3fs-fuse/Makefile.am

Purpose: Top-level automake file for s3fs-fuse, organizing subdirectories and project-wide static-analysis targets.

Important targets and variables: `SUBDIRS=src test doc` controls recursive builds. `EXTRA_DIST=default_commit_hash` packages the generated fallback commit hash. Phony targets `clang-tidy`, `cppcheck`, and `shellcheck` delegate or run analysis. `cppcheck` excludes pjd test directories, enables warning/style/information/missingInclude checks, sets C++ standard from `@CPP_VERSION@`, applies platform defines/undefines, and uses a custom Python addon. `shellcheck` checks both `/bin/sh` and `/bin/bash` scripts discovered by shebang.

Control flow: Normal `make` recurses into src/test/doc. Analysis targets are opt-in and are invoked by CI static-check jobs. `clang-tidy` delegates to `src` and `test`; `cppcheck` runs over `src/ test/`; `shellcheck` finds scripts dynamically and fails on ShellCheck errors.

State and persistence: No runtime state. Generated substitution `@CPP_VERSION@` comes from `configure.ac`; `default_commit_hash` is distributed for non-git builds.

Dependencies and integration points: Integrates autotools output, CI static checks, source and test Makefiles, ShellCheck, cppcheck, and a repo-local addon script.

Risks: Dynamic `find | xargs grep` can behave poorly if no files match, though current repo likely has scripts. Suppressions can hide some style findings. The cppcheck ignore for pjd tests depends on directory naming.

Test signals: `autoreconf/configure && make`, `make cppcheck`, `make shellcheck`, and `make clang-tidy` validate this file's behavior.
<!-- END_FILE_RESEARCH: sources/user-network-fs/s3fs-fuse/Makefile.am -->
