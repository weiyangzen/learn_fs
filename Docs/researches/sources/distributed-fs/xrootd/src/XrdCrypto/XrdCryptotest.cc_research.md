## sources/distributed-fs/xrootd/src/XrdCrypto/XrdCryptotest.cc

### Purpose
This is a standalone diagnostic program for the XrdCrypto factory abstraction. It exercises message digests, symmetric ciphers, bucket encryption, key derivation, RSA generation/import/export/encryption, key-agreement cipher setup, and a small X509 load path.

### Important APIs, Types, and Functions
- `main(int argc, char **argv)` selects a crypto module, defaults to `ssl`, obtains `XrdCryptoFactory::GetCryptoFactory`, and runs all checks in sequence.
- Uses `XrdCryptoMsgDigest::Update`, `Final`, and `AsHexString` with MD5.
- Uses `XrdCryptoCipher` creation by cipher name and key-agreement forms, plus `Encrypt`, `Decrypt`, `EncOutLength`, `DecOutLength`, `Public`, and `Finalize`.
- Uses `XrdCryptoKDFun_t` from the factory and compares deterministic expected strings for local and ssl providers.
- Uses `XrdCryptoRSA` generation, copy construction through the factory, public/private export/import, public/private encryption pairs, and `XrdSutBucket` encryption helpers.

### Control Flow
The program enables verbose SUT and crypto tracing, extracts the executable basename for output, chooses a factory module, and then proceeds linearly. Each feature block creates an object, performs a known operation, compares the result to a literal expected value or round-trip result, prints success or mismatch, and continues. It exits with status 1 only when the factory cannot be loaded or key-agreement public data is unavailable; most feature failures are printed but do not change the process exit code.

### State and Persistence
State is transient and heap allocated. The program prints potentially sensitive RSA private material and cipher data to standard error/stdout for debug purposes. It contains a hard-coded X509 path `/home/ganis/.globus/usercert.pem`, so the X509 block is environment-specific and only runs for factory ID 1.

### Dependencies and Integration Points
This test links against XrdCrypto interfaces and XrdSut helpers. It is useful as a manual smoke test for the factory module selected at runtime, especially `ssl` and `local`. It is not a formal unit test harness and does not appear to be integrated into CTest from this file alone.

### Risks and Edge Cases
The program uses fixed-size stack buffers and `strcpy` for command-line inputs, so long module names or executable names can overflow. It uses weak legacy primitives such as MD5 and 1024-bit RSA for testing. Several allocated objects are not deleted on all branches. It prints private keys, making it unsuitable for normal logs. Because many failures only print messages, automation cannot rely on exit status to determine pass/fail.

### Test Signals
The expected MD5 digest for `"prova"`, KDF outputs for local/ssl, symmetric cipher round trips, RSA import/export and encryption round trips, bucket equality checks, and key-agreement cipher equality are the observable pass signals. A stronger modern test would convert these into assertions with deterministic exit status and avoid printing secrets.
