# File Research: sources/virtualization/nbdkit/plugins/ocaml/Makefile.am

## Purpose
Builds OCaml plugin support: the `NBDKit` OCaml interface artifacts, the `libnbdkitocaml` support library, and an example OCaml plugin.

## Main Contents
Distributes OCaml interface/implementation files, docs, example sources, and the debug-flag C helper. When OCaml is available and the build is not Windows, it compiles `NBDKit.mli`, `NBDKit.ml`, native OCaml objects, and a C support library from `bindings.c`, `buf.c`, `plugin.c`, `plugin.h`, and `callbacks.h`. It also builds `nbdkit-ocamlexample-plugin.so` with `ocamlopt -output-obj -runtime-variant _pic`.

## Dependencies
Gated by `HAVE_OCAML` and `!IS_WINDOWS`; documentation is gated by `HAVE_POD` and `HAVE_OCAMLDOC`.

## Risks and Notes
The support library is not itself an nbdkit plugin; OCaml plugins must link it into their generated shared object. The build is explicitly disabled on Windows, and correctness depends on OCaml native-code toolchain flags such as `OCAML_PLUGIN_LIBRARIES`.
