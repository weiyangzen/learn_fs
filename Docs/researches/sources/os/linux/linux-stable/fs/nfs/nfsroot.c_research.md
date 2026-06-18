# File Research: sources/os/linux/linux-stable/fs/nfs/nfsroot.c

## Purpose

`nfsroot.c` prepares early-boot NFS root mount data. It turns DHCP/IP autoconfiguration data and the `nfsroot=` kernel command-line parameter into the device string and mount option string consumed by the normal NFS mount path.

It is init-only setup code for mounting the root filesystem over NFS.

## Main Responsibilities

- Registers the `nfsroot=` boot parameter parser.
- Optionally registers `nfsrootdebug` under `NFS_DEBUG`.
- Maintains init-time buffers for:
  - raw `nfsroot=` parameters,
  - NFS mount options,
  - server address,
  - export path,
  - final `server:/path` device string.
- Combines defaults, DHCP option 17 root path, command-line overrides, and mandatory NFS root options.
- Returns prepared mount strings via `nfs_root_data()`.

## Defaults and Configuration

Default export path:

- `NFS_ROOT` is `"/tftpboot/%s"`.
- `%s` is replaced late by `utsname()->nodename`, which IP autoconfiguration has already set.

Default mount options depend on kernel config:

- NFSv2: `vers=2,tcp,rsize=4096,wsize=4096`
- NFSv3: `vers=3,tcp,rsize=4096,wsize=4096`
- Otherwise NFSv4: `vers=4,tcp,rsize=4096,wsize=4096`

Mandatory options appended last:

- `nolock`
- `addr=<server IPv4 address>`

Appending these last makes them override earlier options.

## Boot Parameter Parsing

`nfs_root_setup()` handles:

```text
nfsroot=[<server-ip>:]<root-dir>[,<nfs-options>]
```

Behavior:

- Sets `ROOT_DEV = Root_NFS`.
- If the argument starts with `/`, `,`, or a digit, it is copied directly into `nfs_root_parms`.
- Otherwise it treats the string as a hostname-like token and formats it into the default path pattern.
- Calls `root_nfs_parse_addr()` to extract an optional NFS server IP and remove it from `nfs_root_parms`.
- Stores the extracted address in global `root_server_addr`.

## Option and Path Assembly

`root_nfs_parse_options()` splits an incoming string at the first comma:

- The first field is the export path.
- A non-empty path other than `"default"` replaces the current export path.
- Remaining comma-separated text is appended to `nfs_root_options`.

`root_nfs_data()` performs late assembly:

1. Allocates a temporary path buffer.
2. Starts with default `NFS_ROOT`.
3. Applies DHCPv4 option 17 from `root_server_path`, if present.
4. Applies command-line `nfsroot=` options, if present.
5. Appends mandatory `nolock,addr=<server>`.
6. Substitutes `utsname()->nodename` into the export path.
7. Builds `nfs_root_device` as `<server-ip>:<export-path>`.

## Public Entry Point

`nfs_root_data(char **root_device, char **root_data)`:

- Copies `root_server_addr` into local init data `servaddr`.
- Fails if no server address was discovered.
- Calls internal `root_nfs_data()`.
- On success, returns:
  - `*root_device = nfs_root_device`
  - `*root_data = nfs_root_options`

## Error Handling

The file reports and returns `-1` for:

- Missing server address.
- Temporary buffer allocation failure.
- Mount option string overflow.
- Export/device string overflow.

String copying uses `strscpy()` and `strlcat()` wrappers that detect truncation.

## Dependencies

- IP autoconfiguration globals from `<net/ipconfig.h>`, including `root_server_addr` and `root_server_path`.
- NFS mount internals from `internal.h`.
- `utsname()->nodename` for late `%s` substitution.
- `ROOT_DEV` and `Root_NFS` to select NFS root.

## Research Notes

This file is intentionally small but boot-critical. Its main invariant is precedence: built-in defaults first, DHCP option 17 next, command-line `nfsroot=` after that, and mandatory root-NFS options last.
