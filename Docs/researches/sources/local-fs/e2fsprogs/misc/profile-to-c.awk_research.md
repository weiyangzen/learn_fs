# File Research: sources/local-fs/e2fsprogs/misc/profile-to-c.awk

`profile-to-c.awk` converts a profile/config file into a C string constant.

Behavior:
- Emits `const char *mke2fs_default_profile =`.
- For each input line:
  - escapes double quotes,
  - prints the line as a quoted C string with trailing `\n`.
- Emits the final semicolon.

Research notes:
- This script is used to embed the default `mke2fs.conf` profile into the binary, allowing `mke2fs.c` to fall back to `mke2fs_default_profile` when no config file exists.
- It performs only minimal escaping for quotes; backslashes are passed through as-is.
