<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/backend/iclouddrive/api/srp_test.go -->
## Research: sources/user-network-fs/rclone/backend/iclouddrive/api/srp_test.go

### Purpose
`srp_test.go` is a pure unit test suite for Apple's SRP implementation. It validates arithmetic helpers, password derivation variants, proof construction, challenge processing, invalid inputs, and group/hash constants without network access.

### Important APIs, Types, and Functions
The tests cover `padToN`, `getMultiplier`, `derivePassword`, `calculateX`, `calculateU`, `calculateK`, `calculateM1`, `calculateM2`, `newSRPClient`, `srpClient.processChallenge`, `srpN`, `srpG`, `srpNLenBytes`, and `srpHash`.

### Control Flow
Most tests compute expected values manually using the same primitives and compare them to helper outputs. `TestProcessChallenge` uses fixed client and server secrets to build a valid synthetic `B = (k*v + g^b) mod N`, runs `processChallenge`, checks that `M1`, `M2`, and `K` are populated and deterministic, then independently computes the server-side shared secret `(A * v^u)^b mod N` to prove both sides derive the same key.

### State and Persistence
The tests use fixed in-memory values for deterministic checks except `TestNewSRPClient`, which expects two generated clients to have different random secrets. No persistent state is involved.

### Dependencies and Integration Points
The suite uses `crypto/sha256`, `encoding/hex`, `math/big`, `testing`, and `testify`. It protects the `Session.SignIn` authentication path, because any mismatch in these helpers would break iCloud login.

### Risks and Edge Cases Covered
Coverage includes zero padding, values already the size of `N`, deterministic multiplier and proof construction, distinct `s2k` vs `s2k_fo` PBKDF2 inputs, unsupported protocol errors, invalid server `B=0` and `B=N`, known group prefix, generator value, and hash compatibility with standard SHA-256. The tests are arithmetic-heavy but do not use live Apple vectors, so compatibility still depends on Apple's protocol not changing.

### Test Signals
This is high-value cryptographic regression coverage. Failing tests should be treated as authentication-breaking unless the Apple SRP protocol or implementation requirements have intentionally changed.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/backend/iclouddrive/api/srp_test.go -->
