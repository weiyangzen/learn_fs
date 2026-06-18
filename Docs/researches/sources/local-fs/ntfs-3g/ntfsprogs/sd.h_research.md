# File Research: sources/local-fs/ntfs-3g/ntfsprogs/sd.h

## Purpose
Header declaring the security descriptor construction helpers implemented in `sd.c`.

## Exports
- `init_system_file_sd(int sys_file_no, u8 **sd_val, int *sd_val_len)`
- `init_root_sd(u8 **sd_val, int *sd_val_len)`
- `init_secure_sds(char *sd_val)`

## Notes
- Includes `types.h` for `u8`.
- No structs, constants, or ownership annotations are declared here; callers must know from `sd.c` comments that some returned descriptor buffers are static and must not be freed.
