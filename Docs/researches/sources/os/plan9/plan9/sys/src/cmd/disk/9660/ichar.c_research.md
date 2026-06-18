# File Research: sources/os/plan9/plan9/sys/src/cmd/disk/9660/ichar.c

ISO 9660 character/name handling and primary volume descriptor writer.

`isostring` converts fixed-width ISO strings to lowercase atomized Plan 9 strings, trimming trailing spaces. `isisofrog` and `isbadiso9660` enforce the tool’s ISO name policy: lowercase letters/digits/underscore only, 8.3 constraints, and avoidance of generated `Ddddddd`/`Fdddddd` names.

`isocmp` compares conforming names in ISO base/extension order, matching ISO semantics more closely than a plain string compare. `mkisostring` uppercases Plan 9 lowercase names and pads fixed fields.

`Cputisopvd` writes the primary volume descriptor, including system identifier flags (`plan 9`, `rrip`, `boot`, `iso9660` or `utf8`), volume metadata, placeholder sizes/path tables/root directory, dates, and file structure version.

Integration points: used by descriptor read/write, name validation/conversion, and directory sorting.

Risks and notes: this tool treats lowercase source names as canonical and uppercases only when writing ISO fields, so uppercase input names are considered non-conforming. FAT-like generated conform names are reserved.
