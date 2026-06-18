<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/libsmb2/libsmb2.pc.in -->
# sources/user-network-fs/libsmb2/libsmb2.pc.in

Purpose: Pkg-config template describing how downstream projects compile and link against libsmb2.

Important APIs, types, and functions: Defines `prefix`, `exec_prefix`, `libdir`, `includedir`, package metadata, `Libs: -L${libdir} -lsmb2`, and `Cflags: -I${includedir}`.

Control flow: Autotools substitutes install paths and version fields, then installs the resulting `.pc` file for pkg-config consumers.

State and persistence behavior: No runtime state. Installed metadata persists in the target pkg-config directory.

Dependencies and integration points: Integrated with build/install packaging and downstream build systems. It assumes headers are visible directly from `${includedir}`.

Risks: `Requires` is empty, so private dependencies needed for static linking may not be advertised. Include path must match installed header layout from the package.

Test signals: Validated by packaging/install checks rather than runtime tests.
<!-- END_FILE_RESEARCH: sources/user-network-fs/libsmb2/libsmb2.pc.in -->
