# File Research: sources/local-fs/e2fsprogs/misc/findfs.8.in

## Purpose
Manpage source for `findfs`, which locates a filesystem device by label or UUID.

## Key Elements
Documents `findfs LABEL=<label>` and `findfs UUID=<uuid>`, stating that matching device names are printed to stdout.

## Dependencies
Documentation references e2fsprogs packaging and `fsck(8)`.

## Behavior/Risks
Documentation-only. The real lookup behavior depends on system disk probing and label/UUID uniqueness.
