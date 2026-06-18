# File Research: sources/virtualization/nbdkit/plugins/cc/Makefile.am

This Automake file builds the `cc` plugin on non-Windows platforms, because the implementation requires `mkstemps`, dynamic loading, and shell commands. It compiles `cc.c` with configured `CC_PLUGIN_CC` and `CC_PLUGIN_CFLAGS` embedded as preprocessor strings.

The module includes public/generated headers, common include files, common utilities, and the local build directory. It links common utilities, the platform import library, and dynamic loader libraries `$(DL_LIBS)`. Optional plugin symbol versioning uses `plugins/plugins.syms`.

Documentation generation builds a section 3 man page from `nbdkit-cc-plugin.pod`, replacing OCaml include/library placeholders in the POD output.
