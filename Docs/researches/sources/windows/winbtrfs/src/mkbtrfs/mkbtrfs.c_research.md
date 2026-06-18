# File Research: sources/windows/winbtrfs/src/mkbtrfs/mkbtrfs.c

## Purpose

`mkbtrfs.c` is the command-line Btrfs formatting utility for WinBtrfs. It parses user options, loads `ubtrfs.dll`, configures format feature flags and checksum type through exported setter functions, then invokes the DLL's `FormatEx` entry point.

## Entry Points

- `main(int argc, char** argv)`: full CLI flow.
- `print_string(FILE* f, int resid, ...)`: loads localized strings from resources, formats them, and prints to stdout/stderr.

## CLI Arguments

Required:

- `device`: drive letter such as `D:` or a device path such as `\Device\Harddisk0\Partition2`.

Optional:

- `label`: filesystem label.

Supported flags:

- `/sectorsize:num`
- `/nodesize:num`
- `/csum:crc32c|xxhash|sha256|blake2`
- `/mixed` / `/notmixed`
- `/extiref` / `/notextiref`
- `/skinnymetadata` / `/notskinnymetadata`
- `/noholes` / `/notnoholes`
- `/freespacetree` / `/notfreespacetree`
- `/blockgrouptree` / `/notblockgrouptree`

## Defaults and Feature Logic

- Default incompat flags include extended inode refs, skinny metadata, and no-holes.
- Default compat-ro flags include free-space cache.
- Default checksum type is CRC32C.
- Enabling block-group-tree forces free-space-tree and no-holes, matching the Linux-side constraint noted in the source comment.
- Enabling free-space-tree also sets the valid free-space-cache compat-ro bit.

## DLL Interface

Loads `ubtrfs.dll`, with debug fallback paths for x86/x64 builds. It resolves and calls:

- `SetSizes`
- `SetIncompatFlags`
- `SetCompatROFlags`
- `SetCsumType`
- `FormatEx`

`FormatEx` receives undocumented format-style structures matching the Windows formatter interface expectations.

## Device and Label Handling

- Drive letters are normalized to `\??\X:`.
- Device paths are converted from OEM code page to UTF-16.
- Labels are converted from OEM code page to UTF-16 if provided.
- Invalid drive syntax prints a localized error and exits.

## Dependencies

- Windows user-mode headers: `windef.h`, `winbase.h`, `winternl.h`, `devioctl.h`, `ntdddisk.h`, string conversion APIs.
- Local `resource.h` for message IDs.
- `../btrfs.h` for Btrfs feature and checksum constants.

## Research Notes

- The utility is intentionally thin; actual filesystem creation lives in `ubtrfs.dll`.
- Error handling is mostly fail-fast with localized messages.
- The `FORMAT_FLAG_*` definitions are present but the parsed CLI does not currently set most of them in `opts`.
