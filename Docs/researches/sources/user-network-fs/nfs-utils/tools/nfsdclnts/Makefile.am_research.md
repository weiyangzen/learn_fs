<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-utils/tools/nfsdclnts/Makefile.am -->
# sources/user-network-fs/nfs-utils/tools/nfsdclnts/Makefile.am

## Purpose

This Automake file packages the Python `nfsdclnts` NFSv4 client-state inspection tool and its manual page.

## Important APIs, Types, and Functions

It declares `PYTHON_FILES = nfsdclnts.py`, `man8_MANS = nfsdclnts.man`, distributes both, and installs `nfsdclnts.py` as executable `$(sbindir)/nfsdclnts`.

## Control Flow

The build treats the script as a runtime file; installation copies it with executable permissions. Maintainer cleanup removes `Makefile.in`.

## State and Persistence Behavior

There is no runtime state here. Persistent effects are installed files and permissions.

## Dependencies and Integration Points

It integrates the procfs/YAML inspection script into nfs-utils administrative tooling.

## Risks and Edge Cases

Runtime dependencies such as Python and PyYAML are not encoded in this Automake fragment, so packaging must supply them separately.

## Test Signals

Install tests should verify executable placement, man page installation, and inclusion of the Python source in distribution archives.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-utils/tools/nfsdclnts/Makefile.am -->
