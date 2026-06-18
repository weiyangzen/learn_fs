## sources/sync-backup/syncthing/lib/protocol/bep_download_progress.go

Purpose: typed Go representation and wire conversion for BEP download progress messages.

Important types/functions: alias `FileDownloadProgressUpdateType` with append/forget constants; `DownloadProgress` with `toWire` and `downloadProgressFromWire`; `FileDownloadProgressUpdate` with `toWire` and `fileDownloadProgressUpdateFromWire`.

Control flow and state: conversions map update slices and convert version vectors and block indexes between Go ints and generated protobuf fields.

Dependencies and integration points: produced by model `sentdownloadstate` and sent over protocol connections to advertise partially available blocks.

Risks: block indexes convert between `int` and protobuf integer widths; extremely large indexes could overflow on narrow platforms, though block counts are bounded by file/block sizes. No nil guard in `downloadProgressFromWire`.

Test signals: indirectly covered by model progress tests and connection tests.
