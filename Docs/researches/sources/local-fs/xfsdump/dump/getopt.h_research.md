# File Research: sources/local-fs/xfsdump/dump/getopt.h

This header centralizes the xfsdump command-line option string and symbolic option-letter constants for modules that call `getopt`.

Key content:
- `GETOPT_CMDSTRING` contains the full recognized option grammar, including options with required arguments.
- Defines option constants for content, drive, media, global logging, inventory, stack sizing, checksums, compatibility, and operator interaction.
- Content-relevant options include `GETOPT_LEVEL`, `GETOPT_SUBTREE`, `GETOPT_RESUME`, `GETOPT_BASED`, `GETOPT_NOINVUPDATE`, `GETOPT_ERASE`, `GETOPT_ALERTPROG`, `GETOPT_NOEXTATTR`, `GETOPT_DUMPASOFFLINE`, `GETOPT_NOUNCHANGEDDIRS`, `GETOPT_EXCLUDEFILES`, and `GETOPT_MAXDUMPFILESIZE`.

Important dependency:
- Multiple modules rely on this one option string so each parser can skip options it does not own while still preserving global getopt behavior.

Maintenance note:
- This file is a coordination point: changing one option letter can affect several modules even when only one module handles the option.
