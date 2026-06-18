# sources/security-integrity/fsverity-utils/lib/libfsverity.pc.in

Purpose: This pkg-config template describes installed `libfsverity` compiler and linker flags for downstream consumers.

Important APIs and fields: It contains template variables for prefix, exec prefix, libdir, includedir, package name, description, version, `Libs`, and `Cflags`.

Control flow and state: The Makefile substitutes variables during build/install. The generated `.pc` file persists installation metadata.

Dependencies and integration points: Used by package managers, application builds, and CI installation checks. It must align with installed header and library paths.

Risks and test signals: Incorrect paths or missing linker flags make downstream builds fail. Signals include `pkg-config --cflags --libs libfsverity` after install and compiling a small consumer against the installed package.
