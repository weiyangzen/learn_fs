# sources/user-network-fs/nfs-utils/support/Makefile.am

Purpose: this Automake file controls recursive builds for support libraries and helper modules used by nfs-utils.

Important variables: `OPTDIRS` begins empty, adds `nfsidmap` under `CONFIG_NFSV4`, and adds `junction` under `CONFIG_JUNCTION`. `SUBDIRS = export include misc nfs nsm reexport $(OPTDIRS)`. `MAINTAINERCLEANFILES = Makefile.in`.

Control flow: Automake recurses into always-built support directories plus feature-conditional directories selected by `configure.ac`.

State and persistence: build outputs are static support libraries/headers in subdirectories; no runtime state is defined here.

Dependencies and integration points: integrates Automake conditionals from `configure.ac` with support components used by tools and daemons.

Risks: feature conditionals must match generated config headers and source expectations. Directory order matters for headers/libraries consumed by later subdirectories.

Test signals: configure with NFSv4 and junction enabled/disabled and verify recursive targets include/exclude `nfsidmap` and `junction` as intended.
