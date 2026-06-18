## sources/object-store/minio-mc/pkg/disk/stat_windows.go

Purpose: Windows implementation stub for `GetFileSystemAttrs`. It returns an empty string and nil error.

Control flow and state are intentionally absent; Windows does not preserve the Unix-style metadata represented by the other platform files. Dependencies are none beyond package compilation. Integration is with cross-platform copy commands that call the function unconditionally. Risks include users expecting `mc cp -a` to preserve Windows attributes, and tests comparing metadata need platform-aware expectations. The empty success return avoids failing operations but can hide unsupported behavior. No direct Windows test is present in the subset.
