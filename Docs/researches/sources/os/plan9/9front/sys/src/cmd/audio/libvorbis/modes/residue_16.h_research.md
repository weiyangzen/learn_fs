# File Research: sources/os/plan9/9front/sys/src/cmd/audio/libvorbis/modes/residue_16.h

Static residue backend templates for 16/22 kHz Vorbis modes.

Important contents:
- Defines stereo residue book blocks `_resbook_16s_0`, `_resbook_16s_1`, and `_resbook_16s_2`.
- Defines stereo residue templates `_res_16s_0`, `_res_16s_1`, and `_res_16s_2`, referencing residue type/config presets, phrase books, and partition books.
- Defines `_mapres_template_16_stereo[3]`, tying nominal mapping templates to the stereo residue templates.
- Defines uncoupled residue book blocks `_resbook_16u_0`, `_resbook_16u_1`, and `_resbook_16u_2`.
- Defines uncoupled residue templates `_res_16u_0`, `_res_16u_1`, and `_res_16u_2`.
- Defines `_mapres_template_16_uncoupled[3]`.

Integration points:
- Consumed by encoder setup code for 16/22 kHz residue/mapping selection.
- References generated codebooks such as `_16c*_...` and `_16u*_...`, plus residue presets like `_residue_44_mid` and mapping presets like `_map_nominal`.

Risk and review signals:
- Static setup only; correctness depends on all referenced generated books and residue presets existing and matching expected dimensions.
- Template type values select coupled vs uncoupled residue behavior, so accidental edits can alter stereo coding behavior.

Filesystem relevance:
- No filesystem logic. It is static Vorbis residue encoding setup data.
