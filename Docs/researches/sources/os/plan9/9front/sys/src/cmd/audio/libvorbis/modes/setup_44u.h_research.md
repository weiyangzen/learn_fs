# File Research: sources/os/plan9/9front/sys/src/cmd/audio/libvorbis/modes/setup_44u.h

Top-level setup template for 44.1/48 kHz uncoupled Vorbis modes.

Important contents:
- Includes `modes/residue_44u.h`.
- Defines 12-point `rate_mapping_44_un`.
- Defines `ve_setup_44_uncoupled`.

Integration points:
- Reuses shared 44 kHz block sizes, quality mapping, psychoacoustic tables, floor books, floors, and floor mappings.
- Uses `_mapres_template_44_uncoupled`.
- Sets coupling/channel mode field to `-1`, marking uncoupled behavior.

Risk and review signals:
- Static setup data only.
- Inclusion order matters because common 44 kHz symbols are not defined here.
- Uses `_psy_stereo_modes_44` despite uncoupled residue; this appears inherited setup behavior and should be treated cautiously if refactoring.

Filesystem relevance:
- No filesystem logic. It is audio encoder setup data.
