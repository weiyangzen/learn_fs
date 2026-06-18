<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-utils/tools/nfsdclddb/Makefile.am -->
# sources/user-network-fs/nfs-utils/tools/nfsdclddb/Makefile.am

## Purpose

This Automake file packages the Python `nfsdclddb` sqlite database maintenance tool and its manual page.

## Important APIs, Types, and Functions

It sets `PYTHON_FILES = nfsdclddb.py`, includes `nfsdclddb.man` in `man8_MANS`, adds both to `EXTRA_DIST`, and installs the Python script as executable `$(sbindir)/nfsdclddb` in `install-data-hook`.

## Control Flow

The build keeps the script as data rather than compiling it, and install copies it with mode `755`. Maintainer cleanup removes generated `Makefile.in`.

## State and Persistence Behavior

No runtime state exists here. The install hook determines the persistent executable path and permissions.

## Dependencies and Integration Points

It integrates the standalone Python sqlite tool with nfs-utils install and documentation paths.

## Risks and Edge Cases

The install hook assumes `$(sbindir)` exists or is created by surrounding install machinery. Since the script is copied directly, shebang correctness and Python dependencies are runtime packaging concerns.

## Test Signals

Validate `make install DESTDIR=...` produces executable `sbindir/nfsdclddb` and installs the man page and distributed Python file.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-utils/tools/nfsdclddb/Makefile.am -->
