# sources/user-network-fs/impacket/tests/misc/test_ntfs_read.py

Purpose: Unit-tests `examples/ntfs-read.py` logic for nonresident data runs, reading, attribute lists, directory walking, and data-size reporting.

Important APIs, types, and functions: Dynamically imports `examples/ntfs-read.py` via `importlib.util`; uses `AttributeNonResident`, `AttributeListEntry`, `AttributeList`, `INODE`, constants `DATA`, `FILE_NAME`, `FILE_NAME_WIN32`, `FILE_NAME_DOS`, `INDEX_ROOT`, plus mock BPB/volume/inode/index fixtures and binary builders.

Control flow: Helper builders synthesize NTFS attribute records. Test classes cover data-run parsing, sparse runs, negative deltas, multi-run VCN ranges, truncated data-run handling, `readVCN`, read clamping/zero-fill/partial offsets, attribute-list entry parsing, attribute-list iteration, directory walk filtering, and `getDataSize`.

State and persistence behavior: Uses `io.BytesIO` as a mock disk volume; no real filesystem or NTFS image is read.

Dependencies and integration points: Integrates example-script parsing logic with generated raw NTFS structures and volume-style reads.

Risks: The tested script has a hyphenated filename and is loaded dynamically, so path assumptions matter. Data-run parsing is complex and failure-prone around signed offsets, sparse regions, and truncation.

Test signals: Strong signal for NTFS nonresident read correctness, sparse zero filling, EOF behavior, attribute-list robustness, directory walk filtering, and initialized/data size distinction.
