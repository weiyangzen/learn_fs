# sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/ozone/om/snapshot/TestOmSnapshotFsoWithoutNativeLib.java

Purpose: This concrete subclass runs the shared snapshot suite for file-system-optimized buckets while forcing native snapshot diff libraries off. It validates the fallback/full-Java diff path for FSO buckets.

Important APIs/types/functions: The class extends `TestOmSnapshot`, uses `BucketLayout.FILE_SYSTEM_OPTIMIZED`, and calls `super(FILE_SYSTEM_OPTIMIZED, false, false, true, false)`.

Control flow: Construction delegates to the abstract base with filesystem paths disabled, force-full-diff disabled, `disableNativeDiff` true, and linked bucket creation disabled. The inherited suite then skips native-only assumptions and exercises fallback snapshot diff behavior.

State and persistence behavior: The inherited tests cover FSO file/directory table checkpoint state, snapshot reads, deletion, restart, stream file/key operations, MPU diff behavior, and snapshot reuse without native RocksDB diff acceleration.

Dependencies and integration points: This subclass integrates the inherited snapshot suite with the `OZONE_OM_SNAPSHOT_DIFF_DISABLE_NATIVE_LIBS` configuration. It is also the canonical non-native FSO entry for heavy tests guarded by `assumeCanonicalConfig(false)`.

Risks and edge cases: Because this mode bypasses native diff, result ordering and performance-sensitive paths can diverge from the native implementation. The subclass is constructor-only, so the main maintenance risk is accidental argument mismatch against the intended matrix.

Test signals: Correctness is shown by inherited snapshot diff, deletion, restart, quota, tag, stream, and MPU assertions passing with native libraries disabled.
