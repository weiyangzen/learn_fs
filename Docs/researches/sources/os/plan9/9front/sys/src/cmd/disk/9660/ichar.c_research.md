# File Research: sources/os/plan9/9front/sys/src/cmd/disk/9660/ichar.c

ISO 9660 character conversion, validation, sorting, and primary volume descriptor writing.

Key behavior:
- `isostring` converts fixed-width ISO strings to lowercase atomized Plan 9 strings, trimming trailing spaces.
- `isisofrog` and `isbadiso9660` enforce lowercase/digit/underscore plus 8.3-style basename/extension constraints in the in-memory naming model.
- `isocmp` implements ISO-style name sorting by basename then extension.
- `mkisostring` uppercases in-memory names and pads fixed descriptor fields.
- `Cputisopvd` writes the primary volume descriptor with system id, volume id, root directory placeholder, volume metadata, dates, and block padding.

Notable dependencies:
- Directory entry writer `Cputisodir`.
- Global `now`.

Research notes:
- The code stores ISO names lowercase internally and uppercases when writing.
- Names matching generated conform patterns like `Ddddddd`/`Fdddddd` are treated as bad to avoid collisions.
