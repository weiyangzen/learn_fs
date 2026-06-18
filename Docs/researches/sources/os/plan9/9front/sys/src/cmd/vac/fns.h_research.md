# File Research: sources/os/plan9/9front/sys/src/cmd/vac/fns.h

Purpose: Declares shared Vac helper interfaces and constants used by the Vac commands and object layer.

Key behavior:
- Declares metadata block functions (`mbunpack`, `mbinsert`, `mbdelete`, `mbpack`, `mballoc`, `mbinit`, `mbsearch`, `mbresize`).
- Declares metadata entry and directory serialization helpers (`meunpack`, `mecmp`, `mecmpnew`, `vdsize`, `vdunpack`, `vdpack`, `vdcleanup`, `vdcopy`).
- Declares internal root construction and qid management helpers (`_vacfileroot`, `_vacfsnextqid`, `vacfsjumpqid`).
- Declares include/exclude pattern helpers (`glob2regexp`, `loadexcludefile`, `includefile`, `excludepattern`).
- Defines `VacDirVersion = 8` and `FossilDirVersion = 9`.

Dependencies:
- Expects types from `vac.h`, `dat.h`, Venti, and regexp headers included by users.

Notable details:
- The version constants show this tree writes Vac directory metadata version 8 while retaining Fossil version 9 support in the packer.
