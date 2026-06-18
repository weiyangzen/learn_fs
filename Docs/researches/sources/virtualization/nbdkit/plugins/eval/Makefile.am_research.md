# File Research: sources/virtualization/nbdkit/plugins/eval/Makefile.am

Automake build definition for the eval plugin.

Key contents:
- Disabled on Windows because it depends on shell scripting.
- Builds `nbdkit-eval-plugin.la`.
- Reuses shell plugin implementation files by creating symlinks to `../sh/call.c`, `methods.c`, and `tmpdir.c`.
- Compiles `eval.c` with shell-plugin headers.
- Links against common utility library and optional import library.
- Generates documentation from `nbdkit-eval-plugin.pod` when POD is available.
