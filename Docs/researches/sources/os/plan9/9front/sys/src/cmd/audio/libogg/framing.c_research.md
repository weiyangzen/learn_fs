# File Research: sources/os/plan9/9front/sys/src/cmd/audio/libogg/framing.c

## Role

This is the libogg framing layer. It turns raw packets into Ogg pages on encode and reconstructs packets from pages on decode. It also implements page metadata accessors, CRC calculation, sync/recovery scanning, logical stream state, and packet extraction.

It is user-space audio container code, not filesystem code.

## Page Helpers

The file provides simple accessors over `ogg_page` headers:

- `ogg_page_version`
- `ogg_page_continued`
- `ogg_page_bos`
- `ogg_page_eos`
- `ogg_page_granulepos`
- `ogg_page_serialno`
- `ogg_page_pageno`
- `ogg_page_packets`

`ogg_page_checksum_set()` computes the Ogg CRC using the static `crc_lookup[256]` table. It zeroes bytes 22-25 before checksumming and then writes the checksum back in little-endian order.

## Encoding Flow

`ogg_stream_init()` allocates an `ogg_stream_state` with body storage, lacing storage, and granule-position storage. `_os_body_expand()` and `_os_lacing_expand()` grow these internal FIFOs defensively.

Packets enter via `ogg_stream_iovecin()` or `ogg_stream_packetin()`:

1. Returned body bytes are compacted.
2. Packet body bytes are copied into `body_data`.
3. Packet length is split into 255-byte lacing values.
4. The first lacing segment is marked with `0x100` for beginning-of-packet.
5. Granule positions and EOS status are recorded.

Pages are produced through `ogg_stream_pageout()`, `ogg_stream_pageout_fill()`, `ogg_stream_flush()`, and `ogg_stream_flush_fill()`, all using `ogg_stream_flush_i()` internally. The flush logic builds the Ogg page header, writes flags for continued/BOS/EOS, serial number, page number, granule position, segment table, body pointer, and CRC.

## Decode and Sync Flow

`ogg_sync_state` buffers raw bytes from an application. The caller obtains writable space through `ogg_sync_buffer()`, fills it, then calls `ogg_sync_wrote()`.

`ogg_sync_pageseek()` searches for a complete valid Ogg page at the current returned offset:

- Validates the `OggS` capture pattern.
- Waits until the fixed header, segment table, and full body are buffered.
- Verifies the page CRC.
- Returns the page through pointers into `ogg_sync_state` storage.
- On sync failure, scans forward to the next possible `O` capture byte and returns a negative skip count.

`ogg_sync_pageout()` wraps this into the public `-1`, `0`, `1` sync API.

## Stream Page Input

`ogg_stream_pagein()` accepts a validated page for a matching serial number. It:

- Compacts returned lacing/body data.
- Rejects serial mismatches and future Ogg versions.
- Detects missing page numbers and inserts a `0x400` hole marker.
- Handles continued-packet pages by skipping orphaned leading segments when needed.
- Copies page body bytes into stream body storage.
- Appends lacing values and granule positions.
- Marks EOS on the final segment when present.

`ogg_stream_packetout()` and `ogg_stream_packetpeek()` share `_packetout()`, which groups lacing segments into complete packets, reports holes as `-1`, and advances or peeks according to the caller's mode.

## State Reset and Cleanup

The file implements `ogg_stream_clear`, `ogg_stream_destroy`, `ogg_stream_reset`, `ogg_stream_reset_serialno`, `ogg_stream_check`, `ogg_stream_eos`, `ogg_sync_clear`, `ogg_sync_destroy`, `ogg_sync_reset`, and `ogg_sync_check`.

`ogg_packet_clear()` frees packet memory and zeroes the packet object; most packets returned by stream APIs point into stream storage and should not be blindly freed unless ownership came from an allocating API.

## Risks and Edge Cases

The critical correctness areas are lacing FIFO accounting, page loss recovery, continued-packet handling, and CRC validation. The code uses sentinel bits in `lacing_vals`: `0x100` for BOS packet, `0x200` for EOS, and `0x400` for stream holes.

Large packets spanning many pages and pages at the 255-segment limit are explicitly handled and self-tested.

## Test Code

Under `_V_SELFTEST`, the file contains an extensive standalone framing test suite. It validates page headers, packet order, page loss behavior, continuation behavior, sync on partial input, recapture after garbage, checksum behavior, and very large packets.
