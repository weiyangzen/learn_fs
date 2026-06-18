# sources/security-integrity/ecryptfs-utils/src/include/ecryptfs.h

Purpose: primary public userspace header for ecryptfs-utils and libecryptfs.

Important APIs/types: defines version feature flags, sizes/constants for salts/signatures/keys/messages/tags, auth token structures shared with the kernel, password/private-key/session-key structures, messaging contexts, key module operation table, key module state, mount context, crypt stat view, and many libecryptfs function prototypes.

Control flow contracts: callers use version checks to choose mount features; decision graph functions gather mount/key options; passphrase/key-module functions insert auth tokens into kernel keyrings; messaging functions initialize `/dev/ecryptfs`, send messages, and run the daemon; wrapping/unwrapping helpers manage wrapped passphrase files.

State/persistence: structures encode key material, signatures, salts, encrypted/decrypted session keys, key module blobs, file metadata, and messaging state. Some APIs operate on keyrings, rc files, signature caches, wrapped passphrase files, shared memory/semaphores, and `/proc` mount data.

Dependencies/integration: libc, Linux types, pthread, termios, syslog, keyutils-backed libecryptfs implementation, daemon, utilities, PAM, key modules, and SWIG wrapper.

Risks: packed auth token layout must match kernel ABI and architecture width expectations. Many APIs pass raw pointers and fixed-size buffers containing secrets; callers must zero/free carefully. Default salt constants and default key module affect security posture.

Test signals: broad compile coverage plus runtime mount/keyring/messaging/passphrase wrapping tests.
