## sources/test-tools/stress-ng/stress-verity.c

Purpose: Implements `verity`, exercising Linux fs-verity enable, measure, readback, and metadata ioctls on temporary files.

Important APIs/types/functions: `stress_verity_info`, `stress_verity`, `hash_info_t`, and shim metadata arg; uses `FS_IOC_ENABLE_VERITY`, `FS_IOC_MEASURE_VERITY`, optional `FS_IOC_READ_VERITY_METADATA`, `FS_IOC_GETFLAGS`, and fs-verity hash algorithm constants.

Control flow: creates a temp file of sparse 64 KiB-offset chunks, writes identifiable 512-byte blocks, fsyncs/syncs, reopens read-only, rotates hash algorithm, enables verity with page-size block size, measures digest, checks `FS_VERITY_FL`, reopens and reads each chunk to validate the first byte, optionally reads verity metadata, unlinks, and increments bogo.

State and persistence: temporary directory/file only; verity state is discarded by unlinking after each iteration.

Dependencies/integration: Linux fsverity headers/ioctls, filesystem support, crypto availability, stress-ng fs usage reporting.

Risks: many filesystems/kernels lack fs-verity or required crypto; errors map to not-implemented/no-resource. Once verity is enabled the file is immutable, so per-iteration unlink/recreate is required.

Test signals: `VERIFY_ALWAYS`; checks verity flag and readback block content.
