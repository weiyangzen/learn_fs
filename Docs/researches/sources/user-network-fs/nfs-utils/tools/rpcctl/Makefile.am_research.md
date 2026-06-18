<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-utils/tools/rpcctl/Makefile.am -->
# sources/user-network-fs/nfs-utils/tools/rpcctl/Makefile.am

## Purpose

This Automake file packages the Python `rpcctl` sysfs administration tool and its manual page.

## Important APIs, Types, and Functions

It declares `PYTHON_FILES = rpcctl.py`, `man8_MANS = rpcctl.man`, distributes both, and installs the script executable as `$(sbindir)/rpcctl`.

## Control Flow

The build preserves the Python source as a script and install copies it with mode `755`.

## State and Persistence Behavior

No build-time runtime state exists. Installed script and man page are persistent artifacts.

## Dependencies and Integration Points

It integrates the sunrpc sysfs control CLI into nfs-utils packaging.

## Risks and Edge Cases

Runtime availability depends on Python 3 and kernel sunrpc sysfs support, neither of which is represented directly in this file.

## Test Signals

Install tests should verify executable placement, permission mode, man page installation, and distribution archive contents.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-utils/tools/rpcctl/Makefile.am -->
