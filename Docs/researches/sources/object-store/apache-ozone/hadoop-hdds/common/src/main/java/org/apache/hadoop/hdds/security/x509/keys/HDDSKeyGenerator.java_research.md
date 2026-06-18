# sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/hdds/security/x509/keys/HDDSKeyGenerator.java

## Purpose
Generates Java `KeyPair` instances for HDDS certificates using security configuration defaults or caller-specified size/algorithm/provider.

## Important APIs and types
`generateKey()` uses configured size, key algorithm, and provider. `generateKey(int)` overrides size only. `generateKey(int, String, String)` calls `KeyPairGenerator.getInstance(algorithm, provider)`, initializes with the requested size, and generates the pair.

## Control flow and state
Instances hold a `SecurityConfig`. No keys are persisted here; generation is in-memory only.

## Dependencies and integration points
Depends on Java security APIs and `SecurityConfig`. Generated pairs are typically persisted by `KeyStorage` and used by certificate bootstrap/CSR code.

## Risks and test signals
Tests should cover configured defaults, unsupported algorithm/provider exceptions, non-default key sizes, and provider initialization via `SecurityConfig`. There is no explicit `SecureRandom` override, so provider defaults apply.
