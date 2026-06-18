# File Research: sources/virtualization/libguestfs/lib/appliance-uefi.c

## Role
Finds UEFI firmware needed to boot the appliance, currently relevant mainly for aarch64.

## Main Flow
- If libvirt firmware autoselection is supported and allows `efi`, returns that firmware string.
- Otherwise scans generated `guestfs_int_uefi_aarch64_firmware` entries for readable code and vars files.
- Copies the vars/NVRAM file to a libguestfs temp path because firmware variables must be writable.
- Uses debug firmware code when verbose mode is enabled and a debug code file is available.
- Returns firmware flags plus code/vars paths.

## Error Semantics
No firmware found is not an error. Copy or command execution failure is an error.

## Filesystem/Storage Relevance
Correct UEFI setup is required to boot appliances on platforms where the filesystem service VM cannot use legacy BIOS.
