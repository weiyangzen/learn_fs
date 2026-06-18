# File Research: sources/virtualization/qemu/block/vhdx.c

`vhdx.c` is QEMU's main Hyper-V VHDX image format driver. It handles probing, header/region/metadata/BAT parsing, log replay integration, read/write, image creation, checking, zero-init reporting, and driver registration. Differencing VHDX files are recognized through metadata but not supported.

The file defines known VHDX region and metadata GUIDs, create options (`log_size`, `block_size`, `block_state_zero`, subformat), `VHDXImageType`, metadata-present flags, and `VHDXSectorInfo`, which carries BAT index, available sectors/bytes, payload file offset, and block offset for translated I/O.

Checksum helpers use CRC32C. `vhdx_update_checksum()` zeroes the checksum field, calculates CRC over a disk-order buffer, stores little-endian CRC, and returns it. `vhdx_checksum_calc()` supports incremental calculation while temporarily zeroing a CRC field. `vhdx_checksum_is_valid()` compares a stored little-endian CRC with a recalculated one. `vhdx_guid_generate()` creates a QEMU UUID and stores it as an MS GUID-compatible struct.

Region overlap tracking is used for safety. `vhdx_region_register()` records file regions, `vhdx_region_check()` rejects overlaps, and `vhdx_region_unregister_all()` frees the list. The header/log/region/BAT areas are checked so payload BAT entries cannot point into metadata/log/header regions.

Open flow starts in `vhdx_open()`. It opens the `"file"` child, initializes mutex/region list, validates the `vhdxfile` signature, creates a per-session GUID for future header updates, parses the two redundant headers with `vhdx_parse_header()`, replays a dirty log with `vhdx_parse_log()`, opens region tables, parses metadata, sets total sectors, calculates BAT entry count and BAT offset, reads and endian-converts the BAT, optionally checks BAT entries unless opening for check, and installs a live-migration blocker.

`vhdx_parse_header()` reads both 64 KiB header blocks, validates the 4 KiB header checksum, imports little-endian fields, accepts version 1 headers with `head` signature, and chooses the highest sequence number. Equal sequence numbers are accepted only if both headers are byte-identical, matching a Disk2VHD compatibility case. The active header's log region is registered. Header updates use `vhdx_update_header()` and `vhdx_update_headers()`, writing the inactive header with a higher sequence number and then doing the process twice so both headers converge.

`vhdx_open_region_tables()` reads the primary region table block, validates its checksum/signature and entry count, imports entries, rejects overlaps, records the BAT and metadata regions by GUID, rejects duplicate required known regions, and fails on unknown required regions. Both BAT and metadata regions are mandatory.

`vhdx_parse_metadata()` reads the metadata table, identifies required entries for file parameters, virtual disk size, page 83 data, logical sector size, and physical sector size, rejects unknown required metadata, rejects duplicate required entries, reads file parameters and sizes, rejects differencing files with parent locators as unsupported, supports only 512-byte logical sectors, validates block size and power-of-two derived values, computes sectors per block and chunk ratio, and caches shift counts.

BAT layout is calculated by `vhdx_calc_bat_entries()`, including sector bitmap entries interleaved by chunk ratio. `vhdx_check_bat_entries()` validates fully-present payload BAT entries against file length, overflow, truncation, and registered regions. `vhdx_block_translate()` maps logical sector ranges to BAT index and file offsets, adjusting for interleaved sector bitmap BAT entries.

Reads are serialized by `s->lock`. `vhdx_co_readv()` loops across payload block boundaries, rejects differencing files, translates sectors, and branches on BAT state. Not-present, undefined, unmapped, v0.95 unmapped, and zero states read as zero. Fully present blocks read from the child file at the translated payload offset. Partially present blocks and unknown states return errors because differencing support is absent.

Writes are also serialized. `vhdx_user_visible_write()` updates data-write GUID in the headers on the first guest-visible write. `vhdx_co_writev()` translates each block, allocates a new payload block for not-present/unmapped/undefined/zero states with `vhdx_allocate_block()`, optionally zero-fills the rest of a newly allocated block when truncation cannot guarantee zeroes, writes user data to the payload, updates the in-memory BAT entry to fully present, and persists the BAT entry through `vhdx_log_write_and_flush()`. On write error after a BAT update, it restores the in-memory BAT state. Fully present blocks are overwritten directly. Partially present/differencing paths return unsupported/error.

Creation writes the full VHDX layout. `vhdx_co_create()` validates maximum 64 TiB image size, log size multiple/minimum, subformat dynamic/fixed, zero-block option, and block size. It opens the target protocol node through a `BlockBackend`, writes the file identifier and UTF-16 creator string, creates two headers with `vhdx_create_new_headers()`, creates region tables and BAT with `vhdx_create_new_region_table()`/`vhdx_create_bat()`, then writes required metadata with `vhdx_create_new_metadata()`. Dynamic images can use zero-state BAT entries; fixed images preallocate data and mark payload blocks fully present. Legacy create options rename old option keys to QAPI keys, create/open the protocol layer, round size/log/block values, and call the QAPI create function.

`vhdx_co_check()` reports a fixed corruption if the log was replayed during open, then validates BAT entries. `vhdx_has_zero_init()` distinguishes fixed images, which inherit child zero-init status, from dynamic images, which read unallocated data as zero. `vhdx_close()` frees headers, BAT, parent entries, log header, migration blocker, and registered regions.

Important risks and invariants:
- Live migration is blocked for VHDX nodes.
- Differencing files and non-512 logical sector sizes are unsupported.
- Metadata/BAT updates rely on the log path for consistency; direct BAT persistence would bypass recovery semantics.
- Header update sequencing and GUID updates are spec-sensitive.
- BAT entries use 1 MiB-aligned file offsets plus low state bits; incorrect masking can point payload data into metadata regions.
