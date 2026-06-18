# File Research: sources/virtualization/guestfs-tools/align/scan.c

## Scope

Implements `virt-alignment-scan`, a read-only tool that reports partition start alignment for supplied disk images/domains or all libvirt domains.

## CLI And Modes

- Supports `-a`, `-d`, `-c`, `--format`, `--blocksize`, `-P`, `--quiet`, `--uuid`, `-v`, `-V`, and trace/help/list-options flags.
- Uses shared `options.c` globals with fixed invariants: `read_only = 1`, `inspector = 0`.
- If no drives are specified, it enumerates all libvirt domains and scans them in parallel with `start_threads`.
- If drives/domains are specified, it treats them as one guest, launches one libguestfs handle, and scans locally.
- `--uuid` is valid only for all-libvirt-domain mode.

## Alignment Logic

- Lists devices, calls `guestfs_part_list` for each, and skips devices with unrecognized disk labels.
- Canonicalizes device names before printing.
- For each partition, reads `part_start` in bytes and computes the power-of-two alignment by counting trailing zero bits.
- Tracks the smallest alignment seen in global `worst_alignment`, protected by a pthread mutex.
- Reports `<4K` as bad, `<64K` as bad for NetApp-style alignment, otherwise OK.
- Exit codes encode worst alignment: `3` for under 4K, `2` for under 64K, `0` otherwise.

## Dependencies And Risks

- Depends on libguestfs partition inspection and optional libvirt domain enumeration.
- Shared global worst alignment must remain mutex-protected because all-domain mode is threaded.
- Partition start of zero is treated as highly aligned, though the comment notes it is unlikely.
