# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/icclib/icc.h

This is the public header for Graeme W. Gill’s icclib 2.01, bundled under Ghostscript. It defines the ICC profile object model, platform integer aliases, shared-library export handling, file and allocator abstraction classes, and includes `icc9809.h` for ICC signature/type definitions.

The header defines in-memory representations and method tables for ICC tag payloads: integer/fixed arrays, XYZ arrays, curves with reverse lookup tables, data/text/date tags, LUTs, measurements, named colors, text descriptions, profile sequences, screening, UCR/BG, viewing conditions, CRD info, video card gamma, and the profile header.

It defines lookup-object APIs for monochrome, matrix, and multidimensional LUT transforms, including forward/backward lookup functions, normalization, absolute/relative color transforms, ranges, white/black points, and lookup-space metadata.

The main `icc` object exposes methods for reading/writing/dumping profiles, finding/adding/renaming/linking/deleting tags, reading all tags, and constructing lookup objects. Utility declarations include tag/string conversion, enum formatting, XYZ/Lab conversion, standard illuminants, pseudo-Hilbert grid traversal, chromatic adaptation, and Delta E calculations.

This is embedded third-party color-management infrastructure rather than Plan 9 filesystem code.
