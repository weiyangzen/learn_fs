# sources/storage-engines/wiredtiger/test/suite/test_tiered23.py

## Purpose
`test_tiered23.py` tests tiered storage behavior when the local storage-source extension injects delays into tiered operations.

## Important APIs, Types, and Functions
The class uses `TieredConfigMixin`, `SimpleDataSet`, and a `tiered_extension_config` override that returns `delay_ms=130,force_delay=3` for local storage. The main method is `test_tiered`.

## Control Flow
For each row count from 10 through 90, the test creates/populates a `SimpleDataSet`, checks it, calls `checkpoint('flush_tier=(enabled)')`, and checks it again. Reusing the same URI with increasing row counts exercises repeated populate and flush cycles under storage-source delay injection.

## State and Persistence Behavior
The test covers tiered data visibility before and after delayed flush operations. It does not inspect object files directly; dataset checks ensure table contents remain correct despite delayed storage-source calls.

## Dependencies and Integration Points
It integrates with local `dir_store` extension delay knobs, tiered flush checkpointing, and dataset population/check helpers.

## Risks and Test Signals
The risk is timing bugs in tiered flush or file-system callbacks when operations are delayed. The signal is successful data verification before and after each flush-tied checkpoint.
