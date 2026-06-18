# File Research: sources/os/plan9/9front/sys/src/cmd/audio/libvorbis/modes/residue_44.h

Static residue template header for 32/44.1/48 kHz stereo-coupled Vorbis encoder modes.

Important contents:
- Includes `vorbis/codec.h`, `backends.h`, and `books/coupled/res_books_stereo.h`.
- Defines three `vorbis_info_residue0` profiles: `_residue_44_low`, `_residue_44_mid`, and `_residue_44_high`, with progressively broader partition/class metrics.
- Defines many `static_bookblock` tables for quality slots `-1` through `9`, split into stereo and stereo-mid variants at low qualities, then higher-rate coupled residue books.
- Defines paired short/long `vorbis_residue_template` arrays `_res_44s_n1` through `_res_44s_9`.
- Exports `_mapres_template_44_stereo`, mapping quality indexes to `_map_nominal` plus the corresponding residue template.

Integration points:
- Included by `setup_44.h`.
- Uses codebooks generated under `books/coupled/`.
- Consumed by encoder setup assembly code through `ve_setup_data_template` mappings.

Risk and review signals:
- Pure static table data; correctness depends on table alignment with included codebooks and mapping expectations.
- Sentinel-like class metric values such as `999`/`157` are tuning data, not bounds checks.
- Any edits can silently alter bitrate/quality behavior across 44.1/48 kHz stereo encodes.

Filesystem relevance:
- No filesystem logic. This is vendored audio codec encoder configuration data.
