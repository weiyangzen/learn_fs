# sources/test-tools/stress-ng/core-smart.c

Purpose: captures S.M.A.R.T. attribute snapshots before and after a stress-ng run and reports disk attribute counters that changed.

Important APIs/types/functions: `stress_smart_start` and `stress_smart_stop` are public. Internal structs model packed SMART raw values, variable-length snapshots, and linked device entries. `stress_smart_data_read` issues the SG_IO SMART command. Diff helpers count and print changed attributes. Device helpers scan `/dev`, filter/sort candidate block devices, and maintain the linked list.

Control flow: when `OPT_FLAGS_SMART` is set and SCSI SG headers are available, start scans `/dev`, skips hidden names and names ending in digits, stats block devices, reads SMART data using a 12-byte ATA PASS-THROUGH command block, and stores successful snapshots. Stop rereads each device, counts changed raw `data` fields by matching attribute IDs, prints a table if any deltas exist, otherwise reports no devices or no changes, then frees all device/snapshot data. Unsupported builds print an availability note.

State and persistence: `smart_devs` is a static linked-list root holding begin/end snapshots between start and stop. The code reads devices but does not intentionally modify them.

Dependencies/integration: depends on SG_IO, SCSI headers, block devices under `/dev`, `shim_stat`, capability checks for root hints, logging, and global option flags.

Risks: device filtering is heuristic and may skip valid partitionless names ending in digits or include non-disk block devices. SMART reads may require root and can fail silently per device. Attribute raw layouts are vendor-specific, so deltas are useful signals but not full health interpretation.

Test signals: unsupported build path, no devices, non-root runs, SG_IO failure, changed mocked SMART attributes, memory cleanup of device lists, and formatting of known/unknown attribute IDs.
