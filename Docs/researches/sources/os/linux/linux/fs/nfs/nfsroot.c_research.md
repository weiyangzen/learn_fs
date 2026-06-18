# File Research: sources/os/linux/linux/fs/nfs/nfsroot.c

## Purpose

`nfsroot.c` prepares early-boot NFS root mount data. It combines DHCP/IP autoconfiguration data and the `nfsroot=` kernel command-line parameter into the device string and mount option string consumed by the normal NFS mount path.

This is init-only setup code for mounting the root filesystem over NFS.

## Main Responsibilities

- Registers the `nfsroot=` boot parameter parser.
- Optionally registers `nfsrootdebug` under `NFS_DEBUG`.
- Maintains init-time buffers for raw `nfsroot=` parameters, NFS mount options, server address, export path, and final `server:/path` device string.
- Combines defaults, DHCP option 17 root path, command-line overrides, and mandatory NFS root options.
- Returns prepared strings through `nfs_root_data()`.

## Defaults

Default export path:

- `NFS_ROOT` is `"/tftpboot/%s"`.
- `%s` is replaced late with `utsname()->nodename`, after IP autoconfiguration has set it.

Default mount options depend on kernel config:

- NFSv2: `vers=2,tcp,rsize=4096,wsize=4096`
- NFSv3: `vers=3,tcp,rsize=4096,wsize=4096`
- Otherwise NFSv4: `vers=4,tcp,rsize=4096,wsize=4096`

Mandatory options appended last:

- `nolock`
- `addr=<server IPv4 address>`

Appending mandatory options last lets them override earlier options.

## Boot Parameter Parsing

`nfs_root_setup()` handles:

```text
nfsroot=[<server-ip>:]<root-dir>[,<nfs-options>]
```

Behavior:

- Sets `ROOT_DEV = Root_NFS`.
- If the argument starts with `/`, `,`, or a digit, it copies the string directly into `nfs_root_parms`.
- Otherwise it treats the value as a hostname-like token and formats it into the default path pattern.
- Calls `root_nfs_parse_addr()` to extract an optional server IP and remove it from `nfs_root_parms`.
- Stores the extracted address in global `root_server_addr`.

## Option and Path Assembly

`root_nfs_parse_options()` splits an incoming string at the first comma:

- The first field is the export path.
- A non-empty path other than `"default"` replaces the current export path.
- Remaining comma-separated text is appended to `nfs_root_options`.

`root_nfs_data()` performs late assembly:

1. Starts with the default export path.
2. Applies DHCPv4 option 17 `root_server_path` if present.
3. Applies command-line `nfsroot=` overrides if present.
4. Appends mandatory `nolock,addr=...`.
5. Expands `%s` in the export path using `utsname()->nodename`.
6. Builds the final `nfs_root_device` string as `<IPv4-address>:<export-path>`.

## Error Handling

The file rejects overlong strings and allocation failures with `-1` plus kernel error messages:

- Could not allocate temporary path buffer.
- Mount options string too long.
- Root device name too long.
- No NFS server address.

String copying/appending is guarded by `strscpy()` and `strlcat()` length checks.

## Cross-File Relationships

- Uses IP autoconfiguration globals from `<net/ipconfig.h>`, including `root_server_addr` and `root_server_path`.
- Uses `root_nfs_parse_addr()` from NFS internal root-mount support.
- Produces strings consumed by the regular NFS text-based mount interface.

## Research Notes

The key behavior is precedence: default path/options, then DHCP root path, then command-line `nfsroot=`, then mandatory NFS-root options. The mandatory options are intentionally appended last.
