# File Research: sources/os/linux/linux-stable/fs/nls/Kconfig

## Purpose
Defines kernel configuration options for Native Language Support, including DOS/Windows codepages, ISO-8859 variants, KOI8, UTF-8, UCS-2 utilities, and Mac codepages used by Apple filesystems.

## Structure
- `menuconfig NLS` enables the base NLS subsystem as built-in or module `nls_base`.
- `NLS_DEFAULT` selects a default charset string, defaulting to `iso8859-1`.
- Many `tristate` options select individual charset/codepage modules.
- The file ends with hidden `NLS_UCS2_UTILS` and `endif # NLS`.

## Relevant Options for This Group
- `NLS_MAC_CELTIC`: Codepage `macceltic`.
- `NLS_MAC_CENTEURO`: Codepage `maccenteuro`.
- `NLS_MAC_CROATIAN`: Codepage `maccroatian`.
- `NLS_MAC_CYRILLIC`: Codepage `maccyrillic`.
- `NLS_MAC_GAELIC`: Codepage `macgaelic`.

The help text says these Mac codepages are for Apple HFS-family filename conversion on Mac partitions; they affect filenames, not file contents.

## Broader Coverage
The config covers:
- DOS codepages: 437, 737, 775, 850, 852, 855, 857, 860, 861, 862, 863, 864, 865, 866, 869, 874, 932, 936, 949, 950, 1250, 1251.
- ASCII.
- ISO-8859: 1, 2, 3, 4, 5, 6, 7, 8 via CP1255 object, 9, 13, 14, 15.
- KOI8-R and KOI8-U/RU.
- Mac Roman, Celtic, Central Europe, Croatian, Cyrillic, Gaelic, Greek, Iceland, Inuit, Romanian, Turkish.
- UTF-8.

## Research Notes
This file is build-time user policy. It does not implement conversion itself; it controls which NLS modules can be compiled and how filesystems can request charset tables at runtime.
