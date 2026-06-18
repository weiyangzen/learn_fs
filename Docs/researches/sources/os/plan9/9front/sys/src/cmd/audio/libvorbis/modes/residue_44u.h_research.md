# File Research: sources/os/plan9/9front/sys/src/cmd/audio/libvorbis/modes/residue_44u.h

Static residue template header for 32/44.1/48 kHz uncoupled Vorbis modes.

Important contents:
- Includes `books/uncoupled/res_books_uncoupled.h`.
- Defines `_residue_44_low_un`, `_residue_44_mid_un`, and `_residue_44_hi_un` residue profiles for uncoupled channels.
- Defines `_map_nominal_u`, a one-submap mapping with no channel coupling.
- Defines uncoupled static bookblocks `_resbook_44u_n1` through `_resbook_44u_9`.
- Defines short/long `vorbis_residue_template` arrays `_res_44u_n1` through `_res_44u_9`.
- Exports `_mapres_template_44_uncoupled`, mapping quality indexes to `_map_nominal_u`.

Integration points:
- Included by `setup_44u.h` and reused indirectly by `setup_32.h` for uncoupled 32 kHz modes.
- Shares psychoacoustic and floor setup with 44 kHz modes while selecting uncoupled residue books.

Risk and review signals:
- Static table data only; wrong partition metrics or book pointers would alter encoder output or fail setup.
- The uncoupled mapping intentionally disables stereo coupling, trading compression efficiency for independent channels.
- Book names vary slightly (`_44u8_p...` vs `_44u8__...` style), so mechanical edits are error-prone.

Filesystem relevance:
- No filesystem logic. It is Vorbis encoder table configuration.
