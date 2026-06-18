<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/cifs-utils/contrib/Makefile.am -->
# sources/user-network-fs/cifs-utils/contrib/Makefile.am

## Purpose

`contrib/Makefile.am` delegates the contrib build subtree to `request-key.d`.

## Important APIs, Types, and Functions

The only build variable is `SUBDIRS = request-key.d`.

## Control Flow

Automake recurses into `contrib/request-key.d` during build, clean, install, and dist targets as appropriate.

## State and Persistence Behavior

No direct state is created here; generated request-key snippets are handled in the child directory.

## Dependencies and Integration Points

It integrates top-level `SUBDIRS = contrib` from `Makefile.am` with request-key configuration template generation.

## Risks and Edge Cases

If new contrib subdirectories are added but not listed here, they will not participate in Automake recursion.

## Test Signals

`make distcheck` and `make -C contrib` should traverse into `request-key.d`.
<!-- END_FILE_RESEARCH: sources/user-network-fs/cifs-utils/contrib/Makefile.am -->
