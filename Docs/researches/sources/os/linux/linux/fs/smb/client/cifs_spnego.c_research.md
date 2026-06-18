# File Research: sources/os/linux/linux/fs/smb/client/cifs_spnego.c

SPNEGO/Kerberos request-key integration for CIFS session setup.

Defines key type `cifs.spnego`, with instantiate/destroy handlers that copy/free upcall payloads. `cifs_spnego_key_vet_description()` rejects userspace-created descriptions unless the current credentials are the private CIFS SPNEGO credentials, because descriptions contain authority-bearing kernel-originated fields.

`cifs_get_spnego_key()` builds a semicolon-delimited request-key description containing upcall version, host, IP address, security mechanism, uid, cred uid, optional username, pid, and upcall target. It then calls `request_key()` under the private `spnego_cred`.

`init_cifs_spnego()` creates a kernel credential with a private `.cifs_spnego` thread keyring, registers the key type, marks the keyring root-clearable, and stores it for scoped upcalls. `exit_cifs_spnego()` revokes the keyring, unregisters the key type, and drops credentials.
