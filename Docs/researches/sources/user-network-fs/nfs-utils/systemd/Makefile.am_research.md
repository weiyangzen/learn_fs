# sources/user-network-fs/nfs-utils/systemd/Makefile.am

Purpose: `systemd/Makefile.am` installs NFS systemd units, udev rules, man pages, and system generators according to configure-time feature flags.

Important build APIs and control flow: `unit_files` starts with common server/client units and conditionally adds idmapd, v4 server, blkmapd, GSS, svcgssd, and nfsdcld units. It builds `nfsroot-generator`, `nfs-server-generator`, and `rpc-pipefs-generator` from common `systemd.c/systemd.h` plus generator sources. Under `INSTALL_SYSTEMD`, `install-data-hook` copies unit files and `60-nfs.rules` to target directories and renames the pipefs mount template to the configured mount unit.

State, dependencies, and integration: It links generators against support libraries for NFS, export parsing, misc, and reexport.

Risks and test signals: Conditional unit lists must stay aligned with configured daemons. Install hooks use plain `cp`, so packaging paths and template substitution matter. Tests should run feature-matrix builds and inspect installed unit/generator names.
