<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-utils/tools/nlmtest/Makefile.am -->
# sources/user-network-fs/nfs-utils/tools/nlmtest/Makefile.am

## Purpose

This Automake fragment distributes the legacy `nlmtest` sources but does not build an installed program.

## Important APIs, Types, and Functions

`EXTRA_DIST` includes `README`, `host.h`, `nlm_prot.x`, and `nlmtest.c`.

## Control Flow

Automake includes these files in release tarballs. No compile or install target is declared here.

## State and Persistence Behavior

No runtime state exists. The persistent effect is source distribution only.

## Dependencies and Integration Points

It keeps a manual NLM test harness and its RPC protocol input available to developers, separate from normal tool builds.

## Risks and Edge Cases

Because the program is not built by default and `nlmtest.c` contains a compile-time `#error`, it can silently rot unless a developer explicitly repairs it.

## Test Signals

Distribution tests should confirm all four files are present. Any attempt to re-enable the tool should add an explicit build target and compile test.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-utils/tools/nlmtest/Makefile.am -->
