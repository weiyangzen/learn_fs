# File Research: sources/virtualization/guestfs-tools/ocaml-link.sh.in

## Role

Configure-time template used to link OCaml programs in Automake builds.

## Behavior

The script accepts an optional `-cclib`/`--cclib` argument, requires `--` before the command, and then executes the supplied OCaml link command with configured runtime PIC option, `-linkpkg`, and `-cclib "@LDFLAGS@ $cclib"` placed last.

If Automake verbose mode is enabled, it echoes the full command before executing it.

## Research Notes

The script exists because Automake cannot otherwise place `-cclib` at the required end of the OCaml linker command line.
