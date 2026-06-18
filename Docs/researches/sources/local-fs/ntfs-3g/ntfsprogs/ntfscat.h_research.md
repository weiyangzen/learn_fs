# File Research: sources/local-fs/ntfs-3g/ntfsprogs/ntfscat.h

## Role

`ntfscat.h` declares the option state shared by the `ntfscat` implementation.

## Contents

- Includes `types.h` and `layout.h` for NTFS scalar and attribute types.
- Defines `struct options` with:
  - `device`: target device/file path;
  - `file`: pathname to display;
  - `inode`: MFT inode selector;
  - `attr`: selected `ATTR_TYPES` value;
  - `attr_name` and `attr_name_len`: selected named stream/attribute name in NTFS Unicode;
  - `force`, `quiet`, `verbose`: command behavior/logging flags;
  - `raw`: bypass MST-aware decoding for raw data output.

## Consumers

`ntfscat.c` owns a static instance of this structure and fills it during command-line parsing before mounting and streaming the requested attribute.
