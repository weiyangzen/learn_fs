<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/backend/iclouddrive/api/srp.go -->
## Research: sources/user-network-fs/rclone/backend/iclouddrive/api/srp.go

### Purpose
`srp.go` implements the client side of Apple's SRP-6a authentication variant for iCloud sign-in. It provides the RFC 5054 2048-bit group parameters, generates the client secret/public value, derives Apple's password key, computes the shared secret, and produces M1/M2 proofs used by `Session.SignIn`.

### Important APIs, Types, and Functions
Package variables define `srpN`, `srpG`, `srpNLenBytes`, and `srpHashFunc`. `srpClient` stores secret `a`, public `A`, multiplier `k`, and output proofs/session key `M1`, `M2`, and `K`. `newSRPClient` uses `crypto/rand` to create a 32-byte secret and compute `A = g^a mod N`. `getABytes` returns `A` padded to the group length. `processChallenge` validates server `B`, computes `x`, `u`, shared secret `S`, key `K`, and proofs.

Helper functions include `derivePassword`, `padToN`, `srpHash`, `hashToInt`, `getMultiplier`, `calculateX`, `calculateU`, `calculateS`, `calculateK`, `calculateM1`, and `calculateM2`.

### Control Flow
The SRP flow begins by generating `a` and `A`. After Apple returns salt, iteration count, protocol, `B`, and challenge `c`, `derivePassword` hashes the password with SHA-256 and runs PBKDF2-SHA256 using either raw SHA-256 bytes (`s2k`) or hex-encoded SHA-256 (`s2k_fo`). `processChallenge` rejects invalid `B <= 0` or `B >= N`, computes `x = H(salt | H(":" | derivedKey))`, computes `u = H(pad(A) | pad(B))`, rejects zero `u`, computes `S = (B - k*g^x)^(a + u*x) mod N`, hashes it into `K`, and builds Apple-style proofs.

### State and Persistence
The SRP client is ephemeral and holds sensitive derived values only in memory during sign-in. No data is persisted by this file. The Apple ID is lowercased by `Client.New` before it reaches the proof calculation path, because Apple's proof expects that client-side normalization.

### Dependencies and Integration Points
This file depends on Go crypto packages (`crypto/rand`, `crypto/sha256`, `crypto/pbkdf2`), `math/big`, and `hash`. It is used only by `session.go`'s `SignIn` flow.

### Risks and Edge Cases
Cryptographic correctness is critical. Padding must be exactly 256 bytes; username omission in `calculateX` is Apple-specific; `calculateM1` uses `H(g) XOR H(N)` with padded `g`; and unsupported password protocols must error rather than guessing. The implementation validates `B` and `u`, but it does not expose server proof verification beyond calculating `M2` for Apple protocol exchange.

### Test Signals
`srp_test.go` extensively validates padding, multiplier determinism, password derivation variants, `x`, `u`, `K`, `M1`, `M2`, random client generation, deterministic challenge processing with a server-side key check, invalid `B` rejection, group constants, and SHA-256 hashing.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/backend/iclouddrive/api/srp.go -->
