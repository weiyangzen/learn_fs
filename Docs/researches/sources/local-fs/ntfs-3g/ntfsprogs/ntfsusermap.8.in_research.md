# File Research: sources/local-fs/ntfs-3g/ntfsprogs/ntfsusermap.8.in

## Purpose
Manual page for `ntfsusermap`, an interactive utility that builds an NTFS-3G `UserMapping` file mapping Windows account SIDs to Linux user/group IDs.

## User-Facing Contract
- Synopsis: `ntfsusermap windows-system-device [other-ntfs-device...]`.
- First device should contain the Windows system whose users are mapped to the current Linux system.
- Additional NTFS devices contain files shared between the same Windows and Linux installations.
- Must run as root.
- Target devices must not be mounted.
- No command options are defined.

## Workflow Documented
- Scans existing Windows-created files and asks which Linux user or group should own them.
- Accepts numeric or symbolic Linux UID/GID.
- Empty answer defers the decision, allowing later files with the same Windows owner/group to be selected.
- Standard Windows users/groups such as Administrator and All Users are implicitly mapped, so the man page warns never to map a Windows user to Linux root.
- Writes `UserMapping` in the current directory.
- User must move `UserMapping` into `.NTFS-3G` at the root of every NTFS filesystem shared with Windows and Linux.
- Mapping only takes effect at mount time, so the volume must be unmounted and mounted again after installing the file.

## Exit Codes
- `0`: no error detected.
- `1`: error detected.

## Notes
- The AUTHORS section names `ntfs-3g.secaudit`, which appears inconsistent with this page and likely came from related NTFS security tooling documentation.
- The man page is important context for `ntfsusermap.c`: the implementation follows this interactive, root-only, unmounted-volume workflow on non-Windows systems.
