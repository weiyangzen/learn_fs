# sources/security-integrity/ecryptfs-utils/src/key_mod/ecryptfs_key_mod_passphrase.c

Purpose: built-in passphrase key module that gathers passphrase/salt values and inserts a passphrase auth token into the kernel keyring.

Important APIs/functions: `tf_passwd`, `tf_pass_file`, `tf_salt`, static `passphrase_param_nodes`, `passphrase_transition`, `ecryptfs_passphrase_get_param_subgraph_trans_node`, `ecryptfs_passphrase_init`, `get_key_mod_ops`, and `passphrase_get_key_mod_ops`.

Control flow: decision graph chooses direct passphrase, passphrase file, or passphrase fd. Password and salt are pushed on the value stack; `tf_salt` defaults salt if absent, converts hex salt to bytes, calls `ecryptfs_add_passphrase_key_to_keyring`, and pushes `ecryptfs_sig=<sig>` for mount options.

State/persistence: uses transient heap strings and parsed option files/fds. It inserts auth token state into the user session keyring; no module blob persistence.

Dependencies/integration: libecryptfs stack/name-value helpers, `parse_options_file`, `free_name_val_pairs`, salt conversion, keyring insertion, syslog.

Risks: default salt is allowed and can weaken passphrase-derived key uniqueness. Secrets are freed but not always wiped. File descriptor mode trusts caller-provided fd integer.

Test signals: mount helper passphrase flows, passphrase file/fd parsing, keyring insertion, and default salt warnings in higher layers.
