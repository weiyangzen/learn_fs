## sources/user-network-fs/go-fuse/fuse/misc_darwin.go

Purpose: Darwin-specific fallback constant for omitting utimens fields.

Important APIs/types/functions: defines `_UTIME_OMIT = -2`.

Control flow: used by timestamp conversion helpers when a time pointer is nil.

State and persistence: none.

Dependencies and integration: supports `UtimeToTimespec` and Darwin file timestamp updates.

Risks and test signals: wrong omit value can accidentally set timestamps instead of preserving them on macOS.
