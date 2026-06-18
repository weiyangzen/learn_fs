# sources/sync-backup/kopia/repo/maintenancestats/typeconversion.go

Purpose: safely converts signed integer counts/sizes to `uint64` for stats fields.

Important APIs/types/functions: `ToUint64` and package-level `negativeValueWarningLimit`.

Control flow: if the input is negative, it logs a throttled warning and returns zero; otherwise it converts to `uint64`.

State/persistence behavior: prevents negative internal size/count values from being serialized as huge unsigned stats values.

Dependencies/integration: used by cleanup and GC stats builders; depends on `rate.Sometimes` for throttled warning logs.

Risks/test signals: negative values are hidden as zero after warning, which avoids bad metrics but may mask upstream bugs. Tests cover min, negative, zero, positive, and max values.
