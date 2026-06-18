# File Research: sources/os/linux/linux/fs/afs/protocol_afs.h

## Purpose
Defines small AFS protocol constants related to fileserver capabilities.

## Main Responsibilities
- Sets the maximum capabilities word count for AFS capability replies.
- Defines AFS3 fileserver capability bits in capability word 0.

## Key Constants
- `AFSCAPABILITIESMAX`: maximum number of words in a capability set, `196`.
- `AFS3_VICED_CAPABILITY_ERRORTRANS`: server uses Unified AFS Error translation.
- `AFS3_VICED_CAPABILITY_64BITFILES`: server supports `FetchData64` and `StoreData64`.
- `AFS3_VICED_CAPABILITY_WRITELOCKACL`: server can lock without lock permission.
- `AFS3_VICED_CAPABILITY_SANEACLS`: ACL sanity capability, marked “don’t use”.

## Important Details
- `fs_probe.c` consumes `AFS3_VICED_CAPABILITY_64BITFILES` to set `AFS_SERVER_FL_HAS_FS64`, which drives 64-bit file data RPC selection in `fsclient.c`.
