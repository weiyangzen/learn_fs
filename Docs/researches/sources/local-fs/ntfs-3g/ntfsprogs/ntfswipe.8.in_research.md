# File Research: sources/local-fs/ntfs-3g/ntfsprogs/ntfswipe.8.in

## Purpose
Manual page for `ntfswipe`, a utility that overwrites unused or recoverable data areas on an NTFS volume with zeroes, selected byte values, or random/pattern data.

## User-Facing Contract
- Synopsis: `ntfswipe [options] device`.
- Primary goal: clear all or selected unused space on an NTFS volume.

## Wiping Modes
- `--all` / `-a`: selects all wipe categories.
- `--directory` / `-d`: wipe unused directory index areas that may contain deleted names.
- `--logfile` / `-l`: wipe `$LogFile`.
- `--mft` / `-m`: wipe MFT slack and unused MFT records.
- `--pagefile` / `-p`: wipe Windows swap file.
- `--tails` / `-t`: wipe allocated cluster tails beyond file logical EOF.
- `--unused` / `-u`: wipe currently unallocated clusters.
- `--unused-fast` / `-U`: wipe unallocated clusters with a faster skip-aware method.
- `--undel` / `-s`: wipe recently deleted but still undeletable file metadata/data remnants.

## Control Options
- `--bytes BYTE-LIST` / `-b`: comma-separated replacement bytes, parsed as octal, decimal, or hex.
- `--count NUM` / `-c`: repeat overwrite count.
- `--force` / `-f`: override defaults such as refusing mounted/dirty volumes.
- `--info` / `-i`: report wipeable space without wiping.
- `--no-action` / `-n`: execute logic without writing.
- `--quiet`, `--verbose`, `--version`, `--help`.

## Compatibility Notes
- `--undel` is documented as incompatible with `--bytes`; implementation enforces this.
- `--all` may use `--unused-fast` if both are supplied.

## Operational Risk
This is destructive by design. The page emphasizes `--force` caution but otherwise presents the tool as a volume-level metadata/free-space sanitation utility.
