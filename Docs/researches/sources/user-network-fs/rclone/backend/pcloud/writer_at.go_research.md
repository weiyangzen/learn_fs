# sources/user-network-fs/rclone/backend/pcloud/writer_at.go

Purpose: implements an experimental random-access writer over pCloud fileops. It is not currently exposed as an rclone feature because the main backend keeps `XOpenWriterAt` disabled and comments note access-denied responses from pCloud.

Important APIs/types/functions: `writerAt` implements `fs.WriterAtCloser`. `WriteAt` writes a buffer at an offset after comparing SHA1 against the remote range. `Close` verifies final size. Helper functions wrap `/file_open`, `/file_checksum`, `/file_pwrite`, and `/file_close`.

Control flow: `XOpenWriterAt` creates an empty file and returns a writer bound to its file ID. Each `WriteAt` creates a single-connection client, opens a descriptor, checks destination range SHA1, skips identical ranges, writes changed data, and closes the descriptor. `Close` polls `NewObject` up to five times to verify size, or sleeps blindly when size is unknown.

State and persistence: writer state is context, target `Fs`, expected size, remote name, and pCloud file ID. Remote state is the target file. No local data cache persists across calls.

Dependencies/integration: depends on pCloud API response types, `rest.Client`, rclone `fs`, SHA1 hashing, and the backend's single-connection OAuth client and retry helpers. pCloud file descriptors are tied to TCP connection affinity.

Risks/test signals: connection affinity makes this fragile under transport changes. Per-write open/check/write/close is expensive. Unknown-size close cannot verify correctness. A close error after a successful write can leave partial success. No direct tests exist because the feature is not enabled.
