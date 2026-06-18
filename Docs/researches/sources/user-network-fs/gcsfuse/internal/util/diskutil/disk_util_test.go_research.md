## sources/user-network-fs/gcsfuse/internal/util/diskutil/disk_util_test.go

Purpose: Tests disk utility rounding and block-size fallback behavior.

Important APIs/types/functions: `TestGetSpeculativeFileSizeOnDisk`, `TestGetVolumeBlockSize_ProperDir`, and `TestGetVolumeBlockSize_InvalidDir`.

Control flow: table-driven rounding cases cover zero/one block size, zero file size, exact block alignment, and round-up. Statfs tests use `t.TempDir()` and a definitely invalid path.

State and persistence behavior: creates a temporary directory; no persistent state.

Dependencies and integration points: validates syscall-backed block size only by positive power-of-two shape, not exact value.

Risks: filesystems can theoretically report non-power-of-two fragment sizes; test assumes common power-of-two behavior.

Test signals: focused coverage for the disk accounting API.
