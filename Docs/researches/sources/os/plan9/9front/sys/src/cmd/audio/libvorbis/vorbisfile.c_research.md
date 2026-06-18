# File Research: sources/os/plan9/9front/sys/src/cmd/audio/libvorbis/vorbisfile.c

Libvorbisfile convenience layer for opening, probing, seeking, decoding, and reading Ogg/Vorbis streams through stdio or caller-supplied callbacks. It supports seekable files, non-seekable streams, chained logical bitstreams, raw/PCM/time seeking, halfrate decode, integer/float PCM reads, and crosslap seeking.

Important contents:
- Defines page input constants `CHUNKSIZE` and `READSIZE`.
- `_get_data()` reads from callback datasource into `ogg_sync_state`.
- `_seek_helper()` seeks callback datasource and resets sync state while tracking absolute stream offset.
- `_get_next_page()`, `_get_prev_page()`, and `_get_prev_page_serial()` implement forward and backward Ogg page search, including serial-number-aware selection.
- `_fetch_headers()` scans BOS pages, identifies Vorbis headers, rejects duplicate serial numbers in initial header sets, and loads the three Vorbis headers.
- `_initial_pcmoffset()` decodes packet block sizes until a granule position is available to determine the first PCM offset for a link.
- `_bisect_forward_serialno()` recursively discovers chained logical streams in a seekable physical bitstream, allocates per-link metadata, and stores offsets, serials, comments, info, and PCM lengths.
- `_make_decode_ready()`, `_decode_clear()`, and `_fetch_and_process_packet()` manage the live decoder state as reading crosses pages, packets, holes, EOF, multiplexed pages, or logical stream boundaries.
- `_ov_open1()` performs partial open/probe and first-link header parsing; `_ov_open2()` completes seekable or streaming setup.
- Public open/probe APIs include `ov_open_callbacks()`, `ov_open()`, `ov_fopen()`, `ov_test_callbacks()`, `ov_test()`, and `ov_test_open()`.
- Public info APIs include `ov_clear()`, `ov_streams()`, `ov_seekable()`, `ov_bitrate()`, `ov_bitrate_instant()`, `ov_serialnumber()`, `ov_raw_total()`, `ov_pcm_total()`, `ov_time_total()`, `ov_raw_tell()`, `ov_pcm_tell()`, `ov_time_tell()`, `ov_info()`, and `ov_comment()`.
- Public seek APIs include `ov_raw_seek()`, `ov_pcm_seek_page()`, `ov_pcm_seek()`, `ov_time_seek()`, `ov_time_seek_page()`, and `_lap` variants.
- Public read APIs include `ov_read_filter()`, `ov_read()`, and `ov_read_float()`.
- Crosslap support is implemented by `_ov_splice()`, `_ov_initset()`, `_ov_initprime()`, `_ov_getlap()`, `ov_crosslap()`, `_ov_64_seek_lap()`, and `_ov_d_seek_lap()`.

Control-flow summary:
- Opening initializes sync and stream state, optionally seeds initial bytes, tests seekability, parses headers, and either completes streaming setup or recursively maps all chains for random access.
- Reading first ensures decoded PCM exists; if not, it fetches/processes packets, initializes decoder state on demand, handles boundaries, then packs float PCM into requested integer format or returns float channel buffers.
- Seeking maps raw, PCM, or time positions to Ogg page/packet positions. PCM seek uses page-granularity seek first, then discards/tracks packets/samples until exact sample alignment is reached.
- Lap seeking captures overlap from the current decode state, performs the requested seek, primes the new position, and splices the old lap into the new lap buffer using Vorbis windows.

Integration points:
- Depends on `vorbis/codec.h`, `vorbis/vorbisfile.h`, `os.h`, `misc.h`, libogg sync/page/stream APIs, and libvorbis synthesis APIs.
- Uses callback-based I/O, with stdio wrappers for `fread`, `fseek`, `fclose`, and `ftell`.
- Calls external `vorbis_window()` for crosslap windowing.

Risk and review signals:
- Backward page search and chained-stream bisection are sensitive to malformed, truncated, multiplexed, or changing streams.
- Seekability requires both seek and tell callbacks; missing tell after a seek-capable open yields `OV_EINVAL`.
- `ov_read_filter()` validates channel count 1..255 and word size, but relies on caller-provided output buffer length being meaningful.
- Integer PCM packing has separate host-endian, requested-endian, signed, unsigned, 8-bit, and 16-bit paths.
- Several malloc paths in crosslap/lap seeking assume allocation success; this is inherited libvorbisfile code style.
- Non-seekable streams expose only current-link information and cannot report totals or seek.

Filesystem relevance:
- Not a filesystem implementation. It performs file/stream I/O through callbacks and stdio, but its domain is Ogg/Vorbis media parsing and decoding.
