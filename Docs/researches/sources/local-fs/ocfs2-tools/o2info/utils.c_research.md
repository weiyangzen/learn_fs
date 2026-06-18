# File Research: sources/local-fs/ocfs2-tools/o2info/utils.c

`utils.c` contains shared helpers for `o2info`: feature flag string conversion, target open/close, method selection, file type naming, permission rendering, uid/gid lookup, timestamp extraction/formatting, and symlink path formatting.

Feature helpers wrap `ocfs2_snprint_feature_flags()` for compat, incompat, and ro-compat bitsets. Open/close chooses either `ocfs2_open()` with heartbeat-device allowance and read-only flags or a plain read-only fd. Method selection uses `stat()` and routes block/character devices to libocfs2.

Formatting helpers emulate `stat(1)` output, including file mode strings, localtime timestamps with nanoseconds, and symlink `path -> target` display. Risk notes include custom KMP code for nanosecond placeholder replacement, unchecked allocation in that path, `readlink()` truncation bounded by `PATH_MAX`, and hard failure if uid/gid names cannot be resolved.
