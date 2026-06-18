# File Research: sources/os/bsd/netbsd-src/lib/libpam/modules/pam_ssh/pam_ssh.c

Read completely: 482 lines.

This PAM module authenticates by decrypting SSH private keys and can start an `ssh-agent` for the session. It tries `.ssh/identity`, `.ssh/id_rsa`, `.ssh/id_dsa`, and `.ssh/id_ecdsa`.

Authentication flow: `pam_sm_authenticate` resolves the user home directory, obtains a passphrase from `PAM_AUTHTOK`, borrows the target user credentials, tries to load known key files, stores successfully loaded keys as PAM data, and records `pam_ssh_have_keys`. With `try_first_pass`, it retries after clearing the token if an existing token unlocked no keys. `nullok` permits empty passphrases for unencrypted keys; otherwise unencrypted keys are rejected.

Key loading uses `sshkey_load_private`; it first tests for unencrypted keys with an empty passphrase so dummy passphrases cannot bypass `nullok`.

Session flow: `pam_sm_open_session` starts `/usr/bin/ssh-agent -s` when keys exist or `want_agent` is set. The child drops gid/groups/uid to the user, redirects output to a pipe, closes file descriptors, and execs ssh-agent. The parent parses `SSH_*=` assignments from agent output into the PAM environment. It then borrows user credentials, connects to the agent using the PAM environment, adds stored keys, and clears key PAM data. `pam_sm_close_session` kills the agent pid from `SSH_AGENT_PID`.

Security/reliability notes: agent output parsing mutates `fgetln` buffers in place and accepts any line beginning `SSH_` with `key=value;`. `pam_ssh_add_keys_to_agent` temporarily replaces global `environ`, which is process-global and unsafe in threaded PAM consumers.
