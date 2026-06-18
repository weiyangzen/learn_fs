# File Research: sources/local-fs/jfsutils/install-sh

Portable install helper script from Automake/X Consortium lineage.

Key contents:
- Shell script version `2009-04-28.21`.
- Supports installing files, installing into target directory, creating directories, copy-on-change, owner/group/mode changes, strip, and `-T`.
- Uses overridable command environment variables such as `CHGRPPROG`, `CHMODPROG`, `CPPROG`, `MKDIRPROG`, and `STRIPPROG`.
- Implements portable mkdir handling, including POSIX mkdir detection and slow fallback for old systems.
- Installs through temporary files and rename/unlink fallback, with traps for cleanup.
- Supports `--help` and `--version`.

Interactions:
- Referenced by generated Makefiles as `install_sh`.

Research notes:
- Third-party/generated infrastructure file, not JFS-specific logic.
