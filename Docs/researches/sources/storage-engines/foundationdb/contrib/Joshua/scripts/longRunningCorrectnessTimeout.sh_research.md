# sources/storage-engines/foundationdb/contrib/Joshua/scripts/longRunningCorrectnessTimeout.sh

Purpose: timeout companion for long-running correctness jobs. It runs `test_harness.timeout` with `--long-running` so generated timeout summaries carry long-running context.

Important APIs and control flow: no shell functions. It delegates argument parsing to the Python config layer, where `--long-running` affects `Summary.done()` timeout diagnostics.

State and persistence: reads existing trace artifacts from the current working directory and writes summaries to stdout.

Dependencies and integration: requires Python module importability and trace files left by an interrupted long-running job.

Risks and test signals: if no trace files exist, no summaries are emitted. Test with a killed long-running trace directory and verify `ExternalTimeout LongRunning="1"`-style attributes are present.
