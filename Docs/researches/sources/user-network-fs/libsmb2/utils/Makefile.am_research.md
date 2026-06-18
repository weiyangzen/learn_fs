<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/libsmb2/utils/Makefile.am -->
# sources/user-network-fs/libsmb2/utils/Makefile.am

Purpose: Automake rules for installing libsmb2 command-line utilities.

Important APIs, types, and functions: Sets include paths, warning flags, `bin_PROGRAMS = smb2-ls smb2-cp`, per-program sources, and links both tools with `../lib/libsmb2.la`.

Control flow: Automake compiles the utility sources and links them against the in-tree libsmb2 library.

State and persistence behavior: No runtime state; build outputs are binaries in the build/install tree.

Dependencies and integration points: Integrates utils with the library and tests that call `../utils/smb2-cp` and `../utils/smb2-ls`.

Risks: Only two utilities are listed, so new tools must be added explicitly. Include path layout must match source tree headers.

Test signals: Build success and shell tests provide signals.
<!-- END_FILE_RESEARCH: sources/user-network-fs/libsmb2/utils/Makefile.am -->
