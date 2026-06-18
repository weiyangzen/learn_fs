# File Research: sources/os/plan9/9front/sys/src/cmd/gs/jpeg/install-sh

Portable shell install helper derived from X11R5.

Key points:
- Provides BSD-install-like behavior for one file or one directory at a time, avoiding the filename `install.sh` where make implicit rules might create an `install` target artifact.
- Supports dry-run behavior through `DOITPROG`, configurable tool variables (`MVPROG`, `CPPROG`, `CHMODPROG`, `CHOWNPROG`, `CHGRPPROG`, `STRIPPROG`, `RMPROG`, `MKDIRPROG`), and options `-c`, `-d`, `-m`, `-o`, `-g`, `-s`, `-t=...`, and `-b=...`.
- Parses source/destination operands, validates source existence for file installs, treats destination directories by appending the source basename, and derives destination directory with sed.
- Creates missing destination directories component by component using an IFS workaround for old shells.
- Directory mode installs create the directory if absent, then apply owner/group/strip/chmod commands as requested.
- File installs copy or move into a temporary file in the destination directory, set owner/group/strip/chmod options, remove the old destination, then rename the temp file into final position.

Dependencies and interactions:
- Located by `configure` as the auxiliary install script and substituted into generated Makefiles when no suitable system install program is found.
- Used at build/install time only; not part of libjpeg or Ghostscript runtime.

Risk notes:
- Many variable expansions are unquoted, reflecting historical shell portability; paths containing whitespace or shell metacharacters are unsafe.
- The temporary filename uses `#inst.$$#` in the destination directory, so concurrent installs into the same directory by the same PID namespace pattern could collide in unusual conditions.
- The script installs only one file at a time and intentionally preserves old BSD-shell compatibility over modern robustness.
