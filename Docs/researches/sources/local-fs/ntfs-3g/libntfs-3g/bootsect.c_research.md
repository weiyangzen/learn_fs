# File Research: sources/local-fs/ntfs-3g/libntfs-3g/bootsect.c

## Scope

Validates an NTFS boot sector and parses it into `ntfs_volume` geometry fields.

## API And Behavior

- `ntfs_boot_sector_is_ntfs()` verifies the OEM ID signature, bytes per sector range, sectors-per-cluster encoding, maximum cluster size, FAT/reserved BPB fields being zero, MFT/index record cluster-size encodings, non-overlapping positive `$MFT`/`$MFTMirr` LCNs, and optionally logs a warning for a bad `0xaa55` sector marker.
- `ntfs_boot_sector_parse()` populates sector size, cluster size, cluster count, MFT/MFT mirror LCNs, MFT record size, INDX record size, and MFT mirror record count. It validates power-of-two geometry, nonzero sector count, MFT locations within the volume, and seeks to the final sector to catch undersized devices or partition/RAID setup problems.

## State And Dependencies

The parser writes directly into `ntfs_volume`, uses the device operation table for the final-sector seek, relies on little-endian boot sector fields, and logs detailed diagnostics for invalid geometry.

## Risks And Invariants

Validation and parsing are split: callers should run signature/format validation before trusting parsed fields. The final-sector seek is a practical device-size check, not a data read. Negative boot-sector encodings for MFT/INDX record sizes are interpreted as powers of two, matching NTFS format rules.
