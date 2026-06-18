# File Research: sources/os/plan9/plan9/sys/src/cmd/vac/fns.h

Purpose: internal function declarations shared across Vac implementation files.

Contents:
- Declares metablock operations: `mbunpack`, `mbinsert`, `mbdelete`, `mbpack`, `mballoc`, `mbinit`, `mbsearch`, and `mbresize`.
- Declares metaentry comparison/unpacking: `meunpack`, `mecmp`, `mecmpnew`.
- Defines metadata directory versions: `VacDirVersion = 8`, `FossilDirVersion = 9`.
- Declares Vac directory packing helpers: `vdsize`, `vdunpack`, `vdpack`.
- Exposes internal root/qid functions `_vacfileroot`, `_vacfsnextqid`, and `vacfsjumpqid`.
- Declares glob/exclusion helpers used by `vac.c` and tested by `testinc.c`.

Integration points:
- Included by `file.c`, `pack.c`, `glob.c`, `vac.c`, and `testinc.c`.
- Keeps internal helpers out of public `vac.h` while still sharing them within the Vac command implementation.

Risks:
- Version constants are format-level contracts; changing them affects on-disk Vac metadata compatibility.
