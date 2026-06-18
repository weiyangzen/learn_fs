<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/pebble/internal/problemspans/set.go -->
# sources/storage-engines/pebble/internal/problemspans/set.go

Purpose: maintains a set of user-key spans with expiration times, supports overlap checks against non-expired spans, and removes fragments through excision.

Important APIs/types: `Set`, `expirationTime`, `Init`, internal `init`, `boundsToEndpoints`, `Add`, `Overlaps`, `Excise`, `IsEmpty`, `Len`, and `String`.

Control flow and state: `Set` wraps an `axisds/regiontree` keyed by inclusive/exclusive endpoints with `expirationTime` as the property. The property equality function treats any two expired properties as equal to each other and to zero, enabling GC/coalescing as time advances. `Add` updates a bounds interval to the max of existing and new expiration. `Overlaps` asks whether any region in range has expiration greater than current time, with GC enabled. `Excise` sets the interval to zero.

Persistence and integration: in-memory only, with `nowFn` injected for tests and `crtime.NowMono` in production. Dependencies include `axisds`, `regiontree`, and `base.UserKeyBounds`. Risks include no internal synchronization, initialization required before use, careful endpoint conversion for inclusive/exclusive bounds, and expiration cleanup depending on operations. Datadriven and randomized tests cross-check against a naive model.
<!-- END_FILE_RESEARCH: sources/storage-engines/pebble/internal/problemspans/set.go -->
