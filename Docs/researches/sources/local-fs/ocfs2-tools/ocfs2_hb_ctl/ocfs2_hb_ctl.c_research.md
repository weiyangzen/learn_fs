# File Research: sources/local-fs/ocfs2-tools/ocfs2_hb_ctl/ocfs2_hb_ctl.c

`ocfs2_hb_ctl.c` starts/stops OCFS2 local heartbeat regions, reports heartbeat reference counts, and adjusts heartbeat thread I/O priority. It can identify a region by device or UUID; UUID lookup scans `/proc/partitions`, filters IDE non-disk devices, opens candidates with libocfs2, and compares heartbeat descriptors.

Descriptor handling reads heartbeat and cluster descriptions from the OCFS2 volume, duplicates embedded strings, and frees them carefully. Start calls `o2cb_begin_group_join()` and immediately `o2cb_complete_group_join()` for manual starts; stop calls `o2cb_group_leave()`; priority uses `o2cb_get_hb_thread_pid()` and executes `/usr/bin/ionice`.

The main path initializes OCFS2/O2DL/O2CB error tables, validates option combinations, fills UUID from device when needed, blocks most signals during heartbeat action, and frees allocated option strings/descriptors. Risks include hardcoded `/proc/partitions` probing, string allocation ownership complexity, and external `ionice` dependency.
