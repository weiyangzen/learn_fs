# sources/sync-backup/rsync/shconfig.in

Purpose: Autoconf template for shell variables consumed by rsync test scripts and `runtests.py`.

Important APIs, types, and functions: Defines `ECHO_T`, `ECHO_N`, `ECHO_C`, `HOST_OS`, `SHELL_PATH`, and `FAKEROOT_PATH` placeholders and exports them.

Control flow: No branches. `config.status` substitutes `@...@` values to create `shconfig`, and scripts source/read it.

State and persistence behavior: Generated `shconfig` persists build-environment facts for later test execution. The template itself has no runtime state.

Dependencies and integration points: Depends on autoconf substitution from configure. `runtests.py` reads the generated file and injects non-empty values into test environments.

Risks and test signals: Risks include missing substitutions, shell quoting issues, and stale generated `shconfig` after configure changes. Test by running configure, inspecting `shconfig`, and executing tests that depend on fakeroot/shell/echo behavior.
