# File Research: sources/virtualization/guestfs-tools/ocaml-dep.sh.in

## Role

Configure-time template for generating `.depend` files for OCaml subdirectories.

## Behavior

The script wraps `ocamldep -all -one-line`. It defines shared OCaml include directories, derives relative source/build paths with configured `realpath`, builds include flags for the current subdir plus common OCaml libraries, writes `.depend-t`, rewrites absolute source paths into build-relative dependency targets with `sed`, marks the temporary file read-only, and renames it to `.depend`.

## Research Notes

The path rewriting is the important behavior: generated objects and `_config.ml` files are redirected to builddir locations while source references remain relative and stable for Automake includes.
