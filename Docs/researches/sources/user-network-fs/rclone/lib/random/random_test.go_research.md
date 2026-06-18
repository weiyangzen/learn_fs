# sources/user-network-fs/rclone/lib/random/random_test.go

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/lib/random/random_test.go -->
## sources/user-network-fs/rclone/lib/random/random_test.go

Purpose: validates random string and password helpers at the public API level.

Important APIs and control flow: `TestStringLength` checks `String(i)` returns exactly `i` bytes for sizes 0 through 99. `TestStringDuplicates` samples 100 eight-byte strings and asserts no duplicate in the sample. `TestPasswordLength` verifies base64 output length for requested bit sizes 0 through 128. `TestPasswordDuplicates` samples 100 64-bit passwords and asserts uniqueness in the sample.

State, dependencies, and integration: tests depend on real `crypto/rand` through the public helpers and use `testify/assert` and `require`. They do not use deterministic random readers.

Risks and test signals: duplicate tests are probabilistic smoke tests rather than formal distribution checks. The tests do not cover `StringFn` read failures or `Password` entropy source errors.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/lib/random/random_test.go -->
