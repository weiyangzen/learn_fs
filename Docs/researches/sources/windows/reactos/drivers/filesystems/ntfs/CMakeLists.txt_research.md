# File Research: sources/windows/reactos/drivers/filesystems/ntfs/CMakeLists.txt

## Purpose
Build definition for the ReactOS NTFS kernel-mode filesystem driver module.

## Main Responsibilities
- Defines the NTFS driver source list:
  - Attribute handling, block device, B-tree, cleanup/close/create, device control, directory control, dispatch, fast I/O, FCB, file info, FSCTL, MFT, misc, main NTFS code, read/write, volume info, and `ntfs.h`.
- Builds `ntfs` as a module with `ntfs.rc`.
- Sets module type to `kernelmodedriver`.
- Links against `${PSEH_LIB}`.
- Imports `ntoskrnl` and `hal`.
- Adds precompiled header `ntfs.h`.
- Installs the built driver to `reactos/system32/drivers`.

## Important Interactions
- Includes `attrib.c`, the large attribute implementation in this group.
- The PSEH dependency is required by files such as `attrib.c`, which use `_SEH2_TRY`/`_SEH2_EXCEPT`.

## Risks / Review Notes
- No conditional source selection is present; all listed files are part of the driver module.
