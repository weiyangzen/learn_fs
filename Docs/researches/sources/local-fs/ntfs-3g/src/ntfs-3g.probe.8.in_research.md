# File Research: sources/local-fs/ntfs-3g/src/ntfs-3g.probe.8.in

## Role

`ntfs-3g.probe.8.in` is the manual page template for `ntfs-3g.probe`, the helper utility that checks whether an NTFS volume can be mounted read-only or read-write. The `.in` suffix indicates build-time substitution, notably `@VERSION@`.

## Documented Interface

The synopsis is:

`ntfs-3g.probe <--readonly|--readwrite> volume`

The page documents:

- `-r`, `--readonly`: test read-only mountability.
- `-w`, `--readwrite`: test read-write mountability.
- `-h`, `--help`: display help and exit.

The example tests read-write mountability of `/dev/sda1`.

## Exit Codes

The man page defines the user-visible status contract:

- `0`: volume is mountable.
- `11`: syntax error.
- `12`: invalid NTFS.
- `13`: inconsistent NTFS, hardware/device fault, or unconfigured RAID.
- `14`: hibernated NTFS.
- `15`: volume not cleanly unmounted.
- `16`: already exclusively opened or in use.
- `17`: unconfigured SoftRAID/FakeRAID hardware.
- `18`: unknown reason.
- `19`: insufficient privilege.
- `20`: out of memory.
- `21`: unclassified FUSE error.

These correspond to `NTFS_VOLUME_*` status values returned by libntfs/NTFS-3G helper code.

## Relationship To Code

The documented options match `ntfs-3g.probe.c`:

- The command requires exactly one probe mode and one device/image.
- The utility exits with the value returned by `ntfs_volume_error(errno)` after a mount attempt.
- For read-only probe mode, the implementation mounts with `NTFS_MNT_RDONLY`; read-write mode uses normal mount flags.

## Notable Limitations And Risk Areas

- The man page says the tool tests mountability, not filesystem health or repair.
- Exit codes are part of external integration behavior; scripts may depend on these exact numeric meanings.
- The known-issues section points users to the NTFS-3G FAQ and issue tracker rather than documenting detailed remediation per status.
