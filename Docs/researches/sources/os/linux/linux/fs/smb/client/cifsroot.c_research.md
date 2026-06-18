# File Research: sources/os/linux/linux/fs/smb/client/cifsroot.c

## Purpose
`cifsroot.c` implements early boot support for using a CIFS/SMB share as the root filesystem via the `cifsroot=` kernel command-line option.

## Main Data
- `DEFAULT_MNT_OPTS`: default mount options:
  - `vers=1.0`
  - `cifsacl`
  - `mfsymlinks`
  - `rsize=1048576`
  - `wsize=65536`
  - `uid=0,gid=0`
  - `hard`
  - `rootfs`
- `root_dev[2048]`: parsed UNC path.
- `root_opts[1024]`: default options plus user-provided options.

## Important Functions
- `parse_srvaddr()`: extracts IPv4 digits/dots from the server portion and converts with `in_aton()`. IPv6 is explicitly marked TODO.
- `cifs_root_setup()`: parses `cifsroot=//<server-ip>/<share>[,options]`, sets `ROOT_DEV = Root_CIFS`, stores UNC path, parses server address, and appends optional mount options.
- `cifs_root_data()`: returns parsed root device and options to rootfs mounting code, or errors if missing/invalid server address.

## Command-Line Behavior
Registered with:
- `__setup("cifsroot=", cifs_root_setup)`

The parser accepts a UNC-like `//server/share` form and optional comma-separated mount options after the share path.

## Validation and Limits
- Rejects missing share path.
- Rejects UNC path longer than `root_dev`.
- Rejects mount option string longer than `root_opts`.
- Requires parsed server address not equal to `INADDR_NONE`.
- Only IPv4 address extraction is supported.

## Role in the Group
This file is separate from normal runtime VFS registration. It supplies boot-time root filesystem data so the CIFS filesystem registered elsewhere can mount the specified SMB share as `/`.
