# File Research: sources/local-fs/mtd-utils/ubi-utils/include/libiniparser.h

## Role
Public API for the vendored INI parser.

## Main Contents
- Declares section enumeration, dumping, typed getters, setters/unsetters, entry existence check, load, and free functions.
- Exposes compatibility macros `iniparser_getstr` and `iniparser_setstr`.
- Keys are represented as `section:key`.

## Interfaces And Dependencies
- Includes `dictionary.h`.
- Implemented by `libiniparser.c`.

## Notes
- Header declares `iniparser_setstring`, while implementation defines `iniparser_set`; this mismatch is notable in this snapshot.
- Documents parser behavior including integer parsing through `strtol` and boolean first-character matching.
