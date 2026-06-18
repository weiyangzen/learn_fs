# sources/security-integrity/ecryptfs-utils/src/key_mod/ecryptfs_key_mod_gpg.c

Purpose: partial/disabled GPGME key module skeleton for eCryptfs public-key support.

Important APIs/functions: defines `key_mod_gpg`, stub serialization/deserialization, key metadata, generate/encrypt/decrypt stubs, GPG key listing transition functions, `gpg_transition`, `ecryptfs_gpg_init`, and `get_key_mod_ops()`.

Control flow: entering the subgraph allocates a GPGME context and starts key listing. `tf_gpg_keysig` iterates keys/subkeys and fills transition values with subkey key IDs. However `ecryptfs_gpg_init()` returns `-EINVAL` after setting alias, explicitly disabling the module.

State/persistence: intended state includes GPGME context, selected key signature, eCryptfs signature, and serialized blob. Current serialize/deserialize stubs do not persist meaningful data.

Dependencies/integration: GPGME, passwd/getuid, syslog, decision graph, ecryptfs key module ops.

Risks: many TODOs/stubs, incomplete memory cleanup for GPGME keys, and disabled init make it nonfunctional. If enabled without completion, encryption/decryption would falsely succeed or fail unpredictably.

Test signals: build-only when `--enable-gpg`; no meaningful runtime behavior until implemented.
