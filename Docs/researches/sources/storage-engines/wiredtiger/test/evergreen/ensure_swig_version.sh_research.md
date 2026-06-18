<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/evergreen/ensure_swig_version.sh -->
# sources/storage-engines/wiredtiger/test/evergreen/ensure_swig_version.sh

Purpose: source-only setup script that ensures `swig` version 4.0.0 or later is available on `PATH` for WiredTiger builds.

Control flow: defines required version `4.0.0` and install version `4.2.1`, obtains the current version using `swig -version | awk`, and compares with `sort -V`. If current SWIG is new enough it prints a confirmation. Otherwise it creates a Python virtualenv, activates it, installs `swig==4.2.1` from pip, and prints the resulting version.

State and persistence: may create/activate `venv` in the current directory and mutate the caller's environment, which is why the header says it must be sourced rather than executed.

Dependencies and integration: sourced during Evergreen configure/build paths and spawn-host setup. Depends on `swig` being callable enough to report a version or on pip package availability.

Risks and test signals: if `swig` is absent, the command substitution may produce an empty version and comparison behavior depends on shell utilities. It intentionally changes caller `PATH` via virtualenv activation. The script has no shebang and assumes Bash because it uses `[[ ]]`.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/evergreen/ensure_swig_version.sh -->
