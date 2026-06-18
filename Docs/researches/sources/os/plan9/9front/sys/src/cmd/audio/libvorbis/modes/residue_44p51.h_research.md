# File Research: sources/os/plan9/9front/sys/src/cmd/audio/libvorbis/modes/residue_44p51.h

Static residue and mapping template header for 44.1/48 kHz 5.1 Vorbis encoder modes.

Important contents:
- Includes `books/coupled/res_books_51.h`.
- Defines multichannel residue profiles `_residue_44p_lo`, `_residue_44p`, `_residue_44p_hi`, and `_residue_44p_lfe`.
- Defines main-channel residue bookblocks `_resbook_44p_n1` through `_resbook_44p_9`.
- Defines separate LFE bookblocks `_resbook_44p_ln1` through `_resbook_44p_l9`.
- Defines `_map_nominal_51` with coupling steps `{2,4,1,3}` and `_map_nominal_51u` with coupling disabled.
- Defines `_res_44p51_n1` through `_res_44p51_9`; each quality has short, long, and LFE residue templates.
- Exports `_mapres_template_44_51`, switching from coupled mappings at lower quality to uncoupled mappings for qualities 5 through 9.

Integration points:
- Included by `setup_44p51.h`.
- Uses 5.1-specific codebooks and LFE-specific residue coding.
- Depends on Vorbis mapping/residue setup structures from `backends.h`.

Risk and review signals:
- This file is entirely static codec tuning data, but table mismatch can affect 5.1 channel coding, especially LFE.
- Qualities 7-9 reuse `_huff_book__44p6_lfe` and `_resbook_44p_l6` for LFE, which appears intentional tuning reuse.
- Mapping arrays assume six channels and specific Vorbis 5.1 channel layout semantics.

Filesystem relevance:
- No filesystem logic. It is multichannel audio encoder setup data.
