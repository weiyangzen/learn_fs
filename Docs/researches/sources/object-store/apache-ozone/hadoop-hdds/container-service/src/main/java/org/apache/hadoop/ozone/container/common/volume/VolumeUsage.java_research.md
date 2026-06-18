# sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/container/common/volume/VolumeUsage.java

Purpose: Wraps cached filesystem/DU usage for a volume and converts raw filesystem capacity/available/used into Ozone usable capacity and available space after reserved-space accounting.

Important APIs and types: Holds `CachingSpaceUsageSource` and `reservedInBytes`. Key methods include `realUsage`, `getCurrentUsage`, `incrementUsedSpace`, `decrementUsedSpace`, `start`, `shutdown`, `refreshNow`, `getReservedInBytes`, `getUsableSpace`, and static `getOtherUsed`.

Control flow: Construction creates the caching source and computes reserved bytes from either per-directory reserved size config or reserved percent. `getCurrentUsage` returns raw usage when no reservation exists; otherwise it subtracts total reserved from capacity and subtracts only remaining reservation from available space, accounting for non-Ozone usage already consuming reserved space.

State and persistence: Runtime cached usage state only. It reads configuration but writes no files. `shutdownComplete` prevents double shutdown of the source.

Dependencies and integration points: Built by `StorageVolume` from `SpaceUsageCheckParams`. Used by reports, volume choosing, disk balancer calculations, and metrics.

Risks: Directory-specific reserved config compares canonical configured path to the root path string from check params; mismatches can silently fall back to percent reservation. Invalid percent logs and uses default. Tests should cover reserved-byte precedence, malformed reserved entries, percent bounds, other-used math, usable-space helpers, and start/shutdown idempotency.
