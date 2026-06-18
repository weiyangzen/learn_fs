# File Research: sources/os/plan9/9front/sys/src/cmd/audio/libvorbis/vorbisenc.c

High-level libvorbis encoder setup implementation. It selects encoder setup templates, materializes codec setup structs, configures psychoacoustic parameters, floors, residues, mappings, block sizes, bitrate management, and the public `vorbis_encode_*` control/init entry points.

Important contents:
- Defines local setup data structures: `static_bookblock`, `vorbis_residue_template`, `vorbis_mapping_template`, `ve_setup_data_template`, and small psychoacoustic adjustment blocks.
- Includes all encoder mode setup headers: `setup_44.h`, `setup_44u.h`, `setup_44p51.h`, `setup_32.h`, `setup_8.h`, `setup_11.h`, `setup_16.h`, `setup_22.h`, and `setup_X.h`.
- `setup_list[]` orders stereo, 5.1, uncoupled, low-rate, and generic setup templates for template selection by channel count, sample rate, quality, or bitrate.
- `vorbis_encode_floor_setup()` copies floor1 templates, offsets book numbers into the codec setup book table, and installs floor params.
- `vorbis_encode_global_psych_setup()` and `vorbis_encode_global_stereo()` interpolate global pre/post echo thresholds, stereo coupling point limits, and sliding lowpass limits.
- `vorbis_encode_psyset_setup()`, `vorbis_encode_tonemask_setup()`, `vorbis_encode_compand_setup()`, `vorbis_encode_peak_setup()`, `vorbis_encode_noisebias_setup()`, and `vorbis_encode_ath_setup()` populate per-block psychoacoustic parameters from tuning tables.
- `vorbis_encode_residue_setup()` copies residue templates, deduplicates/reuses codebooks, chooses managed/unmanaged books, computes residue end points from lowpass/stereo/LFE limits, and handles residue type 2 bundled-channel sizing.
- `vorbis_encode_map_n_res_setup()` builds one or two mode/map entries depending on whether short and long block sizes differ.
- `get_setup_template()` searches `setup_list[]` for a channel/rate-compatible setup whose quality or bitrate request falls in the template mapping range.
- Public setup/init functions are `vorbis_encode_setup_vbr()`, `vorbis_encode_init_vbr()`, `vorbis_encode_setup_managed()`, `vorbis_encode_init()`, `vorbis_encode_setup_init()`, and `vorbis_encode_ctl()`.

Control-flow summary:
- VBR or managed setup records the request, finds a setup template, initializes high-level defaults, then leaves detailed setup pending.
- `vorbis_encode_setup_init()` freezes the high-level setup, clamps nonsensical ATH/amplitude values, sets block sizes, installs floors, psych parameters, residues/maps, nominal bitrate fields, and bitrate manager state.
- `vorbis_encode_ctl()` can adjust rate management, lowpass, impulse block tuning, and coupling until setup is frozen via `hi->set_in_stone`.

Integration points:
- Depends on `vorbis/codec.h`, `vorbis/vorbisenc.h`, `codec_internal.h`, `os.h`, and `misc.h`.
- Consumes the static setup tables under `modes/` and generated codebooks under `books/`.
- Produces internal `codec_setup_info` state consumed by the rest of libvorbis analysis/encoding.

Risk and review signals:
- Many arrays are indexed by interpolated `base_setting`; correctness depends on template mapping counts matching all tuning arrays.
- `book_dup_or_new()` deduplicates only by pointer identity, so generated/static book pointer stability matters.
- `vorbis_encode_residue_setup()` assumes residue templates use at most 12 partitions and four stages, matching the local `static_bookblock` shape.
- Control calls that mutate setup after `set_in_stone` correctly return `OV_EINVAL`; callers must sequence ctl calls before `vorbis_encode_setup_init()`.
- Residue type 2 end calculation scans installed mappings to infer channel count; mapping/residue setup order is therefore important.

Filesystem relevance:
- No filesystem implementation. This is vendored audio codec encoder configuration code used by 9front audio commands.
