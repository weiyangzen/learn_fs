# sources/user-network-fs/smbj/src/test/groovy/com/hierynomus/test/PredictableRandom.java
# sources/user-network-fs/smbj/src/test/groovy/com/hierynomus/test/PredictableRandom.java

Purpose: deterministic `Random` subclass for tests that need reproducible nonce/challenge bytes. API surface is `init(byte[] bytes)` to set the source byte array and reset index, plus overridden `nextBytes(byte[] bytes)` that copies sequential bytes into the destination.

State and persistence: mutable `randomBytes` and `idx` fields in memory only. Dependencies are `java.util.Random`. Integration point is NTLM crypto tests where client challenges must match protocol examples. Risks include no bounds checks beyond array copy behavior, no thread-safety, and deterministic output unsuitable outside tests. Test signal is helper-level; correctness is inferred through NTLM vector tests.
