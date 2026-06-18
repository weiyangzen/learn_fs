<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/scripting/wscript_build -->
# sources/user-network-fs/samba/source4/scripting/wscript_build

Purpose: Waf build script for installing Samba scripting tools and manpages.

Important APIs/types/functions: `MODE_755`, `bld.CONFIG_SET`, `bld.INSTALL_FILES`, `bld.MANPAGES`, and `bld.RECURSE('bin')`.

Control flow: builds an AD DC script list when AD DC support is enabled, adds `samba-gpupdate` when Python is enabled, optionally installs the manpage, installs `samba-tool` for ADS builds, and recurses into `bin`.

State and persistence behavior: affects installation outputs and permissions, not runtime state.

Dependencies and integration points: ties top-level scripting install layout to `bin/wscript_build` script registration and manpage XML.

Risks: `man_files` is assigned only in the Python-enabled branch but referenced only when `sbin_files` is non-empty and manpage generation is enabled; current flow is safe because `samba-gpupdate` is the documented manpage target. Conditional install lists must stay synchronized with actual files.

Test signals: Waf install output, executable mode `0755`, Python fixups, and generated manpage installation.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/scripting/wscript_build -->
