# sources/storage-engines/tikv/tests/benches/misc/coprocessor/codec/mysql/json/mod.rs

## Purpose
This module benchmarks TiDB JSON binary/text encode and decode paths using a downloaded world-bank JSON corpus.

## Important APIs, Types, and Functions
`download_and_extract_file` streams `curl` output into `tar xzf - --to-stdout` through a helper thread. `load_test_jsons` downloads and splits the corpus into non-empty JSON strings. Ignored benches cover binary encoding with `JsonEncoder`, text encoding through `serde_json`, text parsing into `Json`, and binary decoding with `JsonDecoder`.

## Control Flow
Each ignored bench loads the corpus once, prepares parsed or binary forms as needed, then iterates over every JSON entry inside the measured loop.

## State and Persistence Behavior
State is downloaded data held in memory. No local cache or persistence is implemented.

## Dependencies and Integration Points
It depends on external `curl`/`tar`, network access to PingCAP download resources, `serde_json`, and TiDB JSON codec traits.

## Risks and Test Signals
The benches are ignored because they need network and external tools. Risks include download URL availability, tar format changes, and large memory/time cost. Manual ignored bench runs validate codec performance against a realistic corpus.
