# File Research: sources/os/linux/linux-stable/fs/smb/client/cifsroot.c

Read status: complete.

## Purpose

Implements early-boot CIFS root filesystem support through the `cifsroot=` kernel command-line option.

## Main Responsibilities

- Parse `cifsroot=//<server-ip>/<share>[,options]`.
- Store the root CIFS UNC path and mount options in initdata buffers.
- Extract an IPv4 server address for `root_server_addr`.
- Provide root device and mount option data to the kernel root-mount path.

## Key Data

- `DEFAULT_MNT_OPTS`
  - Default root mount options:
    - `vers=1.0`
    - `cifsacl`
    - `mfsymlinks`
    - `rsize=1048576`
    - `wsize=65536`
    - `uid=0`
    - `gid=0`
    - `hard`
    - `rootfs`

- `root_dev`
  - Stores the parsed UNC device string.

- `root_opts`
  - Stores default options plus user-supplied options appended after the comma.

## Important Functions

- `parse_srvaddr()`
  - Extracts digits and dots from the server portion and converts them with `in_aton()`.
  - IPv6 is explicitly left as TODO.

- `cifs_root_setup()`
  - Registered with `__setup("cifsroot=", ...)`.
  - Marks `ROOT_DEV = Root_CIFS`.
  - Validates and copies the UNC prefix.
  - Parses server address and optional mount options.
  - Bounds-checks both root device and options buffers.

- `cifs_root_data()`
  - Returns the parsed device and options to the root filesystem mount path.
  - Fails when no root device was parsed or the server address is invalid.

## Dependencies

- Uses early boot/root infrastructure from `root_dev.h` and IP autoconfig state from `net/ipconfig.h`.

## Notable Behaviors

- Only IPv4 server address parsing is implemented.
- The function returns `1` from setup parsing even on malformed input, matching `__setup` convention for consuming the option.
- Defaults to SMB1/CIFS root options in this file.
