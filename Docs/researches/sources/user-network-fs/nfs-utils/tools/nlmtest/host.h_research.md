<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-utils/tools/nlmtest/host.h -->
# sources/user-network-fs/nfs-utils/tools/nlmtest/host.h

## Purpose

`host.h` provides local, edit-before-use defaults for the legacy `nlmtest` lock-manager test program.

## Important APIs, Types, and Functions

It defines `NLMTEST_HOST`, `NLMTEST_DIR`, `NLMTEST_FILE`, and `NLMTEST_VERSION`, guarded by `NLMTEST_HOST_H`.

## Control Flow

There is no executable control flow. `nlmtest.c` includes this header to choose the lockd host, NFS mount path, default file, and file-handle version constant.

## State and Persistence Behavior

The values are compile-time constants. Changing them requires editing/rebuilding rather than runtime persistence.

## Dependencies and Integration Points

It integrates the old test harness with a developer's specific NFS test environment. The defaults are placeholders, not portable deployment settings.

## Risks and Edge Cases

The hard-coded host `crutch`, relative mount directory, and version value are unlikely to match modern systems. The comments acknowledge the program cannot discover all file-handle data itself.

## Test Signals

If resurrecting the harness, tests should verify command-line overrides supersede these defaults and that generated file handles match the configured NFS export.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-utils/tools/nlmtest/host.h -->
