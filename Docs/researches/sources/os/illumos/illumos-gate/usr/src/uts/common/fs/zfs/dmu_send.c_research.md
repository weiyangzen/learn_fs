# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/zfs/dmu_send.c

This file implements the send side of ZFS send/receive streams. It traverses datasets, converts changed blocks/dnodes into DMU replay records, writes the stream to a vnode, supports incremental/clone/raw/resume sends, and estimates send sizes.

Core responsibilities:
- Defines send tunables for corrupt-data substitution, queue length, free-record flags, unmodified spill blocks, and estimate recordsize override.
- Writes stream bytes with `dump_bytes()` and maintains stream offset under the dataset sendstream lock.
- Builds checksummed replay records with `dump_record()`, updating Fletcher state and tracking BEGIN/END emission.
- Emits record types:
  - `DRR_FREE` with aggregation for adjacent byte ranges.
  - `DRR_WRITE` for normal, compressed, or raw blocks.
  - `DRR_WRITE_EMBEDDED` for eligible embedded payloads.
  - `DRR_SPILL` for spill blocks, including raw fields and unmodified spill markers.
  - `DRR_FREEOBJECTS` with aggregation.
  - `DRR_OBJECT` for dnode metadata and bonus payloads.
  - `DRR_OBJECT_RANGE` for raw dnode-block encryption metadata.
  - `DRR_BEGIN` / `DRR_END` in `dmu_send_impl()`.
- Handles feature flags for SA spill, large blocks, large dnodes, embedded data, compressed send, raw send, LZ4, and resumable sends.
- Uses `traverse_dataset_resume()` from `dmu_traverse.c` in a producer thread to enqueue block records into a `bqueue`; the main send thread dequeues records, reads data from ARC, and writes replay records.
- Implements block classification in `do_dump()`:
  - Skips special objects and indirect blocks.
  - Converts holes in meta-dnode space to freeobjects.
  - Converts data holes to free ranges.
  - Reads dnode blocks and emits object records.
  - Reads SA/spill blocks and emits spill records.
  - Emits embedded writes when stream features permit.
  - Reads regular blocks as raw, compressed, or normal payloads.
  - Splits large blocks when the receiver did not negotiate large-block support.
- Supports raw encrypted sends by not decrypting traversal data, authenticating objset phys for non-raw encrypted sends, and including encryption parameters in stream records and BEGIN payload.
- Supports resume sends by including resume object/offset in BEGIN payload and starting traversal from the corresponding bookmark.
- Provides public send entry points:
  - `dmu_send_obj()` sends by object IDs within a pool.
  - `dmu_send()` sends by dataset/bookmark names and can own live heads to freeze them during send.
- Provides size estimates:
  - `dmu_send_estimate()` uses dataset accounting or `dsl_dataset_space_written()`.
  - `dmu_send_estimate_from_txg()` traverses blocks born after a TXG.
  - `dmu_adjust_send_estimate_for_indirects()` adjusts data-space estimates for indirect blocks and replay record overhead.

Important control-flow notes:
- `dump_free()` and `dump_write()` enforce increasing object/offset order; receive depends on this for correctness and resumability.
- `dump_dnode()` sends an object record, then a free-to-end marker past maxblkid, and may send unmodified spill blocks for compatibility.
- Raw send implies compressed and large-block-capable stream behavior.
- Non-raw encrypted sends authenticate `os_phys_buf` before sending.
- Send cancellation is coordinated by queue draining and an EOS marker from the traversal thread.
- If `zfs_send_corrupt_data` is enabled, unreadable data blocks can be replaced by a fixed corrupt-data pattern instead of failing.

Key dependencies:
- Dataset traversal callbacks from `dmu_traverse.c`.
- ARC raw/compressed/normal reads for block payload acquisition.
- DSL dataset/bookmark logic for incremental ancestry and clone detection.
- DMU backup record formats in `dmu_send.h` / replay records.
- Crypto helpers for raw send key and block parameter serialization.

Risk-sensitive invariants:
- Feature flags must match the receiver’s capabilities; large blocks, embedded data, LZ4, raw, and compression alter record layout.
- Raw streams must preserve encrypted block metadata exactly.
- Resume sends must begin at the same object/offset expected by the receiver.
- The stream must emit valid BEGIN and END records or verification fails before cleanup.
