# sources/object-store/apache-ozone/hadoop-hdds/framework/src/main/java/org/apache/hadoop/hdds/utils/MetadataKeyFilters.java

## Purpose
`MetadataKeyFilters` provides byte-prefix filtering for metadata DB keys. Its primary built-in helper, `getUnprefixedKeyFilter`, returns a negative filter that hides keys beginning with `#`, following the convention that special key prefixes are surrounded by `#`.

## Important APIs and Types
`KeyPrefixFilter` exposes `filterKey(byte[])`, counters `getKeysScannedNum` and `getKeysHintedNum`, and factories `newFilter(String)` and `newFilter(String, boolean negative)`. A null positive prefix returns a singleton pass-through filter; a null negative prefix is rejected.

## Control Flow and State
Each `filterKey` call increments `keysScanned`; null keys return false. A null prefix returns true. Otherwise `prefixMatch` compares byte-by-byte and the positive/negative flag decides whether matches pass or fail. Passing keys increment `keysHinted`.

## Persistence, Dependencies, and Integration
There is no persistence. It depends on `org.apache.hadoop.hdds.StringUtils` for string-to-byte conversion and is intended for LevelDB/RocksDB metadata scans and prefix-aware table iteration.

## Risks and Test Signals
The source contains a TODO noting two known issues: string conversion can replace unsupported characters with `?`, and the encoding may differ from the key codec. Tests should cover positive and negative filters, null/short keys, counter accuracy, null prefix behavior, and non-ASCII prefixes once codec-aligned filtering is implemented.
