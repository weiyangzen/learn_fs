<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/src/live_restore/live_restore_fs.c -->
# sources/storage-engines/wiredtiger/src/live_restore/live_restore_fs.c

## Purpose
Implements the live-restore `WT_FILE_SYSTEM` and `WT_FILE_HANDLE` wrappers. The wrapper presents the destination home as the active database while lazily reading missing data from a backup source and tracking migrated data-file blocks with bitmaps.

## Important APIs, Types, and Functions
`__wt_os_live_restore_fs` constructs the layered file system. File-system methods include directory listing, existence checks, open, remove, rename, size, and terminate. File-handle methods include read, write, size, sync, truncate, lock, and close. Core helpers include `__live_restore_fs_find_layer`, stop-file creation/checking, backing-path construction, bitmap encode/decode/fill, `__live_restore_can_service_read`, `__live_restore_fill_hole`, `__wti_live_restore_fs_restore_file`, `__wt_live_restore_metadata_to_fh`, `__wt_live_restore_fh_to_metadata`, `__wt_live_restore_clean_metadata_string`, and `__wti_live_restore_cleanup_stop_files`.

## Control Flow
Path translation asserts that incoming paths start with the destination home and maps them to either destination or source. Existence and directory listing are destination-first, hide `.stop` and `.lr_tmp` files, and suppress source files hidden by destination stop files. Opening a data file can open the source, create a same-sized destination placeholder atomically, then open the destination; opening regular/log files copies the whole source file through a temporary destination file and rename. Reads consult the bitmap under a read lock: fully migrated ranges read from destination, holes read from source. Writes go to destination, then set bitmap bits for the written allocation-size range. Background migration repeatedly finds the first clear bitmap bit, reads source chunks, writes destination chunks, and closes the source handle when complete. Remove and rename create stop files so later source entries with the same name remain hidden.

## State and Persistence Behavior
Each live-restore data-file handle owns a bitmap sized to the original source file in allocation-size units. `1` bits mark destination-resident data, clear bits mark holes still served from source. Checkpoint metadata stores `live_restore=(bitmap=<hex>,nbits=<n>)`; `nbits=0` means migration has not started and reconstructs an empty bitmap from destination size, and `nbits=-1` means the file is complete and source can be closed. Temporary files with `.lr_tmp` make atomic copy/create operations crash-tolerant. Stop files with `.stop` persist user delete/rename decisions until cleanup. Cleanup removes stop files after background migration and checkpoints have durably removed live-restore metadata.

## Dependencies and Integration Points
Uses WiredTiger file-system abstractions, POSIX creation for nested directories on Linux/Apple, block/file-handle callbacks, bitstring helpers, scratch buffers, verbose/stat APIs, checkpoint metadata hooks, turtle/state helpers, and connection flags. It is invoked from connection setup, block open, checkpoint metadata serialization, backup cleanup, and the background server. Stats include bytes copied, source-read count, and source-read latency histogram.

## Risks and Edge Cases
Bitmap correctness is central: reads assert the range pattern is `1*0*`, writes/truncates require allocation-size alignment, and crashes after truncation but before metadata persistence are guarded by reopen assertions. Source and destination path handling assumes destination-prefix paths. Rename is intentionally restricted to files already present in destination because partially migrated data files cannot be renamed safely at this layer. Regular/log files are copied on open rather than lazily migrated. The implementation is currently POSIX-only and readonly mode is rejected. Directory listing holds the state lock across both layers to avoid state-change races. Backup cleanup asserts that non-empty bitmaps are not backed up.

## Test Signals
Catch2 API tests cover file existence, open-file behavior, file-handle size/read/write/lock/close/sync/truncate, file-system size, remove/rename, and directory listing. Unit tests cover bitmap encode/decode, bit-range filling, read-end computation, and hole filling through `HAVE_UNITTEST` wrappers. Python suite and cppsuite live-restore tests exercise end-to-end restore, restart, cleanup, stats/progress, backup interactions, and user-visible file-system behavior.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/src/live_restore/live_restore_fs.c -->
