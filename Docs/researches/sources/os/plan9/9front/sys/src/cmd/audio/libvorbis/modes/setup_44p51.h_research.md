# File Research: sources/os/plan9/9front/sys/src/cmd/audio/libvorbis/modes/setup_44p51.h

Top-level setup template for 44.1/48 kHz 5.1 surround Vorbis modes.

Important contents:
- Includes `modes/residue_44p51.h`.
- Defines 12-point `rate_mapping_44p51`.
- Defines `ve_setup_44_51` for six-channel encoding.

Integration points:
- Reuses shared 44 kHz quality mapping, block sizes, psychoacoustic tables, floor books, floors, and floor mappings.
- Uses `_mapres_template_44_51` from `residue_44p51.h`.
- Sets channel/coupling mode field to `6`, matching 5.1 setup expectations.
- Uses floor mapping count `3`, unlike stereo/uncoupled 44 kHz setup count `2`.

Risk and review signals:
- Static setup data only.
- Inclusion order matters because many 44 kHz symbols are assumed from `setup_44.h`.
- Bitrate mapping is much lower per quality point than stereo because values are setup-selection hints, not total transparent quality guarantees.

Filesystem relevance:
- No filesystem logic. It is surround audio encoder preset data.
