<!-- BEGIN_FILE_RESEARCH: sources/object-store/minio/cmd/data-usage-cache_test.go -->
## sources/object-store/minio/cmd/data-usage-cache_test.go

Purpose: This hand-written test file validates object-size histogram behavior used by data usage accounting. It focuses on bucket-label conversion and migration from an older histogram layout.

Important APIs and functions: `TestSizeHistogramToMap` exercises `sizeHistogram.add` and `sizeHistogram.toMap`. `TestMigrateSizeHistogramFromV1` exercises `sizeHistogram.mergeV1`. The tests use `github.com/dustin/go-humanize` constants to place sample object sizes in byte, KiB, MiB, and tens-of-MiB ranges.

Control flow: `TestSizeHistogramToMap` builds a histogram by adding object sizes, converts it to a map of public bucket labels, then checks that expected buckets have exact counts and unexpected buckets are zero or absent. The first case intentionally checks overlapping/coarser labels such as `LESS_THAN_1024_B`, `BETWEEN_64_KB_AND_256_KB`, and `BETWEEN_1024B_AND_1_MB`. `TestMigrateSizeHistogramFromV1` constructs V1 array values and verifies that they map into current histogram indexes, with older buckets shifted into the newer bucket layout.

State and persistence behavior: No files are persisted. The tests target in-memory histogram state, but the behavior matters for persisted `.usage-cache.bin` compatibility because current cache entries store `sizeHistogram`, while older entries may carry `sizeHistogramV1`.

Dependencies and integration points: These tests depend on the histogram definitions and methods in `data-usage-cache.go` and the generated serializers in `data-usage-cache_gen.go` for the persistent representation. The map labels are consumed by `BucketUsageInfo.ObjectSizesHistogram` in data usage API responses.

Risks: The test data covers only a small subset of bucket thresholds. It does not exhaustively assert all histogram labels or boundary values around every threshold, so off-by-one changes in less-common ranges could slip through. Migration checks cover two compact cases but not zero-filled or fully populated edge arrays beyond the shown values.

Test signals: The file provides targeted confidence that the public histogram labels and V1-to-current migration retain expected counts for common small and medium objects.
<!-- END_FILE_RESEARCH: sources/object-store/minio/cmd/data-usage-cache_test.go -->
