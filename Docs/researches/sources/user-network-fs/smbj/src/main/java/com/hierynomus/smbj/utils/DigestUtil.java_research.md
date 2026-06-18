<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smbj/src/main/java/com/hierynomus/smbj/utils/DigestUtil.java -->
# sources/user-network-fs/smbj/src/main/java/com/hierynomus/smbj/utils/DigestUtil.java

Purpose: Utility for chained message digest computation, especially SMB 3.1.1 preauthentication integrity hashing.

Important APIs/types/functions: digest(MessageDigest digest, byte[] previous, byte[] extra) resets the digest, updates with previous then extra, and returns digest.digest().

Control flow: Callers provide an already selected MessageDigest implementation and the two byte arrays to concatenate logically.

State and persistence behavior: Stateless utility, but it mutates the passed MessageDigest state by reset/update/digest.

Dependencies and integration points: Depends on com.hierynomus.security.MessageDigest; used by authentication/connection security code outside this subset.

Risks: Null previous/extra handling depends on MessageDigest.update behavior and can throw. Callers sharing a MessageDigest across threads would race.

Test signals: Known-vector digest of previous plus extra, reset behavior between calls, null input behavior, and thread confinement expectations.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smbj/src/main/java/com/hierynomus/smbj/utils/DigestUtil.java -->
