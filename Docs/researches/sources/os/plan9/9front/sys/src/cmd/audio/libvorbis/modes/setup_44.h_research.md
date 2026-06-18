# File Research: sources/os/plan9/9front/sys/src/cmd/audio/libvorbis/modes/setup_44.h

Primary top-level setup template for 44.1/48 kHz stereo Vorbis modes.

Important contents:
- Includes `modes/floor_all.h`, `modes/residue_44.h`, and `modes/psych_44.h`.
- Defines 12-point stereo bitrate mapping and 12-point quality mapping from `-0.1` to `1.0`.
- Defines 11 short and long block sizes for quality slots.
- Defines short/long companding mappings and `_global_mapping_44`.
- Defines three floor mapping arrays `_floor_mapping_44a`, `_floor_mapping_44b`, `_floor_mapping_44c`.
- Defines `ve_setup_44_stereo`.

Integration points:
- Base setup reused by `setup_32.h`, `setup_44p51.h`, `setup_44u.h`, and `setup_X.h`.
- Binds 44 kHz psychoacoustic tables, floor tables, and coupled residue templates.
- Supplies shared symbols such as `quality_mapping_44`, block sizes, and floor mappings.

Risk and review signals:
- This is a central static table; changes can affect several other setup headers.
- `rate_mapping_44_stereo` ends at `250001`, likely to avoid boundary ambiguity.
- Floor mapping arrays have 11 entries while quality mapping has 12 entries; this matches existing libvorbis setup conventions but is easy to misuse.

Filesystem relevance:
- No filesystem logic. It is encoder preset data.
