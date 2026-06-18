## sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/hdds/client/OzoneQuota.java

Purpose: represents Ozone namespace and byte quotas and parses user-facing quota strings.

Important APIs: `Units` enum from B through EB with byte multipliers and small-value caches; `parseSpaceQuota`, `parseNameSpaceQuota`, `parseQuota`, `getOzoneQuota`, quota getters, raw size/unit getters, and `toString`.

Control flow: space parsing uppercases and removes whitespace, checks unit suffixes in descending unit order to avoid `B` matching `KB`, parses positive integer sizes, and stores raw unit plus computed bytes. Namespace parsing accepts only positive integer counts and stores byte quota as -1 raw bytes. `RawQuotaInBytes.valueOf` converts a byte count to the largest power-of-1024 unit implied by trailing zero bits and asserts exact reconstruction.

State/persistence: object fields are effectively immutable except `quotaInNamespace` is not final. Dependencies: Ozone byte constants, Guava `Strings`, Ratis `Preconditions`.

Integration points: volume/bucket quota CLI/API, metadata display, quota persistence through byte/count values. Risks: multiplication can overflow for large EB values; no explicit negative byte quota except the namespace-only sentinel path; raw conversion assumes Ozone unit sizes are powers of 1024 and indexes `Units.values()` by trailing-zero groups; error text omits newer units PB/EB. Test signals: all unit suffixes, whitespace/case handling, zero/negative rejection, overflow boundaries, exact unit conversion, namespace-only sentinel, and combined quota parsing.
