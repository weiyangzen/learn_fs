# File Research: sources/os/plan9/9front/sys/src/cmd/audio/libvorbis/modes/residue_8.h

Static residue templates for 8/11 kHz Vorbis encoder modes.

Important contents:
- Includes `vorbis/codec.h` and `backends.h`; it relies on residue profiles and mappings defined by earlier included headers.
- Defines stereo bookblocks `_resbook_8s_0` and `_resbook_8s_1`.
- Defines stereo residue templates `_res_8s_0` and `_res_8s_1`, both using `_residue_44_mid`.
- Exports `_mapres_template_8_stereo`.
- Defines uncoupled bookblocks `_resbook_8u_0` and `_resbook_8u_1`.
- Defines uncoupled templates `_res_8u_0` and `_res_8u_1`, using `_residue_44_low_un` and `_residue_44_mid_un`.
- Exports `_mapres_template_8_uncoupled`.

Integration points:
- Included by `setup_8.h`; `setup_11.h` reuses the same 8 kHz residue templates for 11 kHz.
- Depends on `_map_nominal`, `_map_nominal_u`, and residue profile symbols defined in other mode headers.

Risk and review signals:
- Header inclusion order matters because several referenced symbols are not defined locally.
- This low-rate configuration has only two quality classes, so quality interpolation is coarse.
- All content is static encoder tuning data.

Filesystem relevance:
- No filesystem logic. This is audio codec setup data.
