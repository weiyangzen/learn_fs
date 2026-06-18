# sources/object-store/minio/cmd/bitrot_test.go

This test file exercises the bitrot reader/writer factory path for every algorithm registered in `bitrotAlgorithms`. It is the main direct correctness signal for the bitrot files in this subset.

`testBitrotReaderWriterAlgo` creates a temporary local XL storage backend, creates a test volume, constructs a bitrot writer with object length `35` and shard size `10`, writes three full 10-byte chunks and one 5-byte final chunk, closes the writer if it implements `io.Closer`, then constructs the matching reader with `bitrotWriterSum(writer)` and reads offsets `0`, `10`, `20`, and `30`. For streaming algorithms the sum is nil because hashes are embedded per shard; for whole-file algorithms the writer sum is used by the verifier.

`TestAllBitrotAlgorithms` loops over the algorithm registry and calls the helper. This ensures newly registered algorithms get at least basic write/read coverage if they are added to `bitrotAlgorithms`.

State is temporary filesystem state under `t.TempDir`, plus local storage volumes/files. Dependencies include `newLocalXLStorage`, `newBitrotWriter`, `newBitrotReader`, and storage volume creation.

The test covers successful sequential reads with aligned offsets and final short shard handling. It does not intentionally corrupt data or hashes, test unaligned offsets, test short reads, test random access out of order, verify `bitrotVerify` directly, or assert self-test behavior. It is a useful integration smoke test but not exhaustive corruption-detection coverage.
