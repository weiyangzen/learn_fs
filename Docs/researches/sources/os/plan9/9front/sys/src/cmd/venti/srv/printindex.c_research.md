# File Research: sources/os/plan9/9front/sys/src/cmd/venti/srv/printindex.c

`printindex` dumps entries directly from index section buckets. It loads the Venti config, initializes disk cache, optionally filters by index section name, reads every bucket block in selected sections, unpacks `IBucket`, unpacks each `IEntry`, and prints address, score, type, and size.

The tool bypasses high-level lookup and scans raw index storage. It is a diagnostic complement to `printarenas`: differences between the two expose stale, missing, or extra index records.

The file assumes bucket blocks are readable and trusts unpacked bucket counts; deeper validation is done elsewhere by check/sync tools.
