<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/cifs-utils/contrib/request-key.d/Makefile.am -->
# sources/user-network-fs/cifs-utils/contrib/request-key.d/Makefile.am

## Purpose

`contrib/request-key.d/Makefile.am` generates request-key configuration snippets for CIFS idmap and SPNEGO upcalls.

## Important APIs, Types, and Functions

It defines `noinst_DATA = cifs.idmap.conf cifs.spnego.conf`, template substitution rules for both `.conf` files, and `clean-local`.

## Control Flow

Each generated `.conf` target runs `sed` to replace `@sbindir@` in the `.in` template, writes a temporary `-t` file, then atomically moves it into place. `clean-local` removes generated snippets.

## State and Persistence Behavior

The generated snippets are build artifacts and are not installed automatically by this Makefile (`noinst_DATA`).

## Dependencies and Integration Points

It depends on the `SED` Autoconf substitution and the two template files. Administrators or packages can use the generated snippets under request-key configuration.

## Risks and Edge Cases

Since snippets are `noinst`, packagers must explicitly install them if desired. Wrong `sbindir` substitution breaks request-key invocation paths.

## Test Signals

Build tests should verify generated snippets contain the configured helper path and are removed by clean targets.
<!-- END_FILE_RESEARCH: sources/user-network-fs/cifs-utils/contrib/request-key.d/Makefile.am -->
