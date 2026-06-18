# File Research: sources/virtualization/guestfs-tools/win-reg/virt-win-reg.in

Perl implementation and embedded POD for `virt-win-reg`, a tool to export or merge Windows Registry entries from Windows guests.

Key behavior:
- Uses `Sys::Guestfs`, `Win::Hivex`, and `Win::Hivex::Regedit`.
- Supports options: `--help`, `--version`, `--debug`, `--connect`, `--format`, `--merge`, `--encoding`, `--unsafe-printable-strings`, `--long-options`, and `--short-options`.
- In export mode, opens the disk read-only; in merge mode, opens writable and warns in POD that live VM use can corrupt disks.
- Accepts a first positional argument as URI, local disk image, or libvirt domain name.
- For URI-like image arguments, shells out to `guestfish -a URI -x exit` and parses the traced `add_drive` call to reconstruct guestfs add-drive arguments.
- Launches guestfs, inspects OS, rejects no OS or multiboot guests, mounts all detected filesystems read-only for export or writable for merge.
- Determines Windows system root with `inspect_get_windows_systemroot`.
- Uses a temporary directory for downloaded registry hives.
- Export mode:
  - requires registry path and optional value name,
  - maps path to hive,
  - downloads hive,
  - either exports recursively with `reg_export` or calls `hivexget` for a single value.
- Merge mode:
  - imports from stdin or listed `.reg` files using `reg_import`,
  - lazily downloads and opens required hives writable,
  - commits changed hive handles,
  - uploads modified hives back into the guest,
  - shuts down and closes guestfs.
- Registry path mapping supports HKLM SAM, SECURITY, SOFTWARE, SYSTEM; HKU `.DEFAULT`; HKU SID; LocalSystem/LocalService/NetworkService aliases; and HKU username by probing `/Users/<name>` or `/Documents and Settings/<name>`.
- SID profile paths are resolved through `HKLM\SOFTWARE\Microsoft\Windows NT\CurrentVersion\ProfileList\<sid>\ProfileImagePath`, expanding `%systemroot%`, `%systemdrive%`, stripping `C:`, and converting backslashes.
- Hive download/upload uses `case_sensitive_path` and dies with translated errors on failure.

Documentation notes:
- Explains supported Windows NT-derived systems from XP through at least Windows 8.
- Documents unsupported `HKEY_CURRENT_USER` and literal `$SID`.
- Describes Windows 8 fast startup/hibernation caveat.
- Gives encoding conversion examples for UTF-16LE regedit files.
- Explains `CurrentControlSet` alias limitations.
- Documents deletion syntax for keys and values.
- Includes examples for RunOnce scripts and service installation registry edits.

Research notes:
- The URI parsing path is explicitly called a hack in comments.
- `--unsafe-printable-strings` is intentionally lossy and only for quick debugging.
