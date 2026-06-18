# File Research: sources/virtualization/nbdkit/plugins/ocaml/example-debug-flag.c

## Purpose
Demonstrates how an OCaml plugin can expose and read an nbdkit debug flag implemented in C.

## Main Contents
Defines exported integer debug flag `ocamlexample_debug_foo`, set by `-D ocamlexample.foo=<N>`, and exposes `get_ocamlexample_debug_foo()` for OCaml code.

## Dependencies
Uses OCaml `value` API and nbdkit plugin header for DLL visibility/API version.

## Risks and Notes
This is example code intended to be copied. It returns the current global debug flag value without allocation or validation.
