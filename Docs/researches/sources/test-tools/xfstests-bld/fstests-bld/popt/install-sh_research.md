# sources/test-tools/xfstests-bld/fstests-bld/popt/install-sh

## Purpose

`install-sh` is a portable shell implementation of the BSD/X11 `install` utility. The vendored `popt` build uses it when a platform `install` program is absent or unsuitable, allowing generated make install rules to copy files, create directories, set modes, optionally set ownership/group, optionally strip binaries, and avoid replacing an unchanged destination when requested.

The source was read as a complete 520-line shell script. It is generated build infrastructure with direct filesystem side effects during `make install` and related Autotools workflows.

## Important APIs, Types, and Functions

The public interface is:

- `install-sh [OPTION]... [-T] SRCFILE DSTFILE`
- `install-sh [OPTION]... SRCFILES... DIRECTORY`
- `install-sh [OPTION]... -t DIRECTORY SRCFILES...`
- `install-sh [OPTION]... -d DIRECTORIES...`

Supported options are `--help`, `--version`, ignored `-c`, `-C` copy-on-change, `-d` directory creation, `-g GROUP`, `-m MODE`, `-o USER`, `-s`, `-t DIRECTORY`, `-T`, and `--` to end options. The script exposes command overrides through environment variables: `CHGRPPROG`, `CHMODPROG`, `CHOWNPROG`, `CMPPROG`, `CPPROG`, `MKDIRPROG`, `MVPROG`, `RMPROG`, `STRIPPROG`, and `DOITPROG` for dry-run style command echoing.

Important internal state variables include `mode`, `copy_on_change`, `dir_arg`, `dst_arg`, `no_target_directory`, `posix_mkdir`, `posix_glob`, `doit`, `doit_exec`, `cp_umask`, `mkdir_umask`, `dsttmp`, and `rmtmp`. There are no shell functions; behavior is organized by option parsing and a `for src` loop.

## Control Flow

The script initializes IFS, command defaults, desired file mode, and option state. It parses options, validates modes to reject whitespace and glob characters, extracts the destination argument when not using `-d` or `-t`, and exits successfully for empty `install-sh -d` calls because conditional directory variables in Makefiles can expand to nothing.

For each source or directory target, it protects leading-dash names with `./`, resolves whether the destination is a directory, computes `dstdir` with `dirname` or fallback `expr`/`sed`, and tests whether the destination directory already exists. If parent directories are missing, it first probes whether `mkdir -p` behaves safely for the current mode and umask. When that probe fails or a race occurs, it falls back to component-by-component directory creation while tolerating concurrent creators.

With `-d`, it creates/configures directories and then applies optional owner, group, and mode commands. For file installation, it sets a restrictive copy umask based on the requested mode and strip behavior, copies the source to `$dstdir/_inst.$$_`, applies owner/group/strip/chmod to the temp file, compares old and new metadata/content for `-C`, and either discards the unchanged temp or renames it into place. If the first `mv -f` fails, it removes or renames aside the existing destination and retries the move. Exit traps remove temporary files on signal or error paths.

## State and Persistence Behavior

Persistent effects are created directories, installed files, mode changes, ownership/group changes, stripped binaries, and replacement of previous destination files. Temporary files named `_inst.$$_` and `_rm.$$_` are created in the destination directory and removed by traps or explicit cleanup. `-C` preserves the previous destination file and its modification time when file type, owner, group, size metadata, and byte content match.

The script does not write configuration state. However, its filesystem changes persist outside the build tree when install prefixes point to system locations. `DOITPROG` changes execution from direct `exec` for some commands to command-printing or a caller-supplied wrapper, which is useful for dry runs but means state changes depend on the wrapper semantics.

## Dependencies and Integration Points

`install-sh` is integrated by Autoconf/Automake-generated make install rules. Its filename avoids `make` implicit-rule confusion with an `install` target. It depends on `/bin/sh`, `basename`, `dirname` when available, `expr`, `sed`, `ls`, `cmp`, `mkdir`, `cp`, `mv`, `rm`, `chmod`, optional `chown`, optional `chgrp`, and optional `strip`.

The script coordinates with generated `Makefile.in` variables such as `INSTALL`, `INSTALL_PROGRAM`, `INSTALL_DATA`, `MKDIR_P`, and install directories. It is especially relevant for old or non-GNU platforms where `mkdir -p`, `install -C`, or `install -T` behavior differs from modern GNU coreutils.

## Risks and Edge Cases

The implementation deliberately supports old shells and non-POSIX utilities, which makes path handling complex. It has protections for leading dashes and several fallback `dirname` cases, but many operations remain sensitive to unusual paths containing newlines, shell metacharacters, or aggressively nonstandard whitespace. Temporary filenames are based on `$$` in the destination directory; normal build use is low risk, but shared writable install directories can expose collision or symlink-style concerns.

Owner/group operations can fail without sufficient privilege. `strip` requires writable temporary files, so umask calculation is adjusted and can interact with unusual symbolic modes. The `-C` comparison parses `ls -dlL` output fields, which is inherently platform-sensitive. The fallback replacement path may unlink or move aside an old destination before the final move succeeds; a failure at that point can leave the target absent. Directory creation contains explicit concurrency handling, but races remain possible on unusual filesystems.

## Test Signals

Useful smoke tests include installing one data file to an explicit path, installing multiple sources into an existing directory, creating nested directories with `-d`, using `-T` against an existing directory and expecting failure, using `-C` twice and confirming the second run does not replace an identical file, and overriding `DOITPROG=echo` to inspect generated operations. Platform tests should cover requested modes `0644` and `0755`, owner/group behavior when permitted, strip behavior for binaries, concurrent directory creation, missing source and missing destination diagnostics, and paths with leading dashes or spaces to document current support limits.
