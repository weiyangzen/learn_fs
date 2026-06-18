<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-utils/utils/Makefile.am -->
# sources/user-network-fs/nfs-utils/utils/Makefile.am

## Purpose

This Automake file orchestrates which nfs-utils utility subdirectories are built, based on configure-time feature flags.

## Important APIs, Types, and Functions

`OPTDIRS` is conditionally extended for `idmapd`, `nfsidmap`, `exportd`, `blkmapd`, `gssd`, `mount`, `nfsdcld`, `nfsdcltrack`, `nfsref`, and `nfsdctl`. `SUBDIRS` always includes `exportfs`, `mountd`, `nfsd`, `nfsstat`, `showmount`, and `statd`, followed by `$(OPTDIRS)`.

## Control Flow

Automake recurses into the listed subdirectories during build/install. Configure feature variables decide which optional daemons/tools participate.

## State and Persistence Behavior

There is no runtime state. Build/install persistence is determined by which subdirectories produce binaries, config files, and man pages.

## Dependencies and Integration Points

It is the central build integration point for the `utils` subtree and maps configure options to built NFS client/server utilities.

## Risks and Edge Cases

Mandatory subdirectories build regardless of optional feature flags. Optional ordering can matter when subdirectories depend on generated headers or support libraries, so changes to `OPTDIRS` order should be reviewed.

## Test Signals

Configure/build matrices should toggle each feature flag and verify expected subdirectories are included or excluded, with `make dist` and `make install` still succeeding.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-utils/utils/Makefile.am -->
