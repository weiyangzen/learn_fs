# File Research: sources/os/linux/linux-stable/fs/smb/client/cifs_spnego.c

## Purpose

Implements CIFS SPNEGO request-key integration for Kerberos-like session setup, including a private key type, private credential/keyring setup, authority-checked key descriptions, and construction of cifs.upcall request descriptions.

## Main Responsibilities

- Defines key type `cifs.spnego`:
  - `cifs_spnego_key_instantiate()` duplicates upcall payload into key storage.
  - `cifs_spnego_key_destroy()` frees payload.
  - `cifs_spnego_key_vet_description()` rejects userspace-created descriptions unless current credentials are the private CIFS SPNEGO credentials.
  - Uses `user_describe()` for key description.
- Implements `cifs_get_spnego_key()`:
  - Builds a key description containing upcall version, hostname, server IP, selected security mechanism, linux uid, credential uid, optional username, pid, and upcall target.
  - Supports IPv4 and IPv6 server addresses.
  - Selects `sec=krb5`, `sec=mskrb5`, or `sec=iakerb`, defaulting to `krb5` if server auth flags are unknown.
  - Calls `request_key()` under `spnego_cred`.
  - Traces Kerberos auth result and optionally dumps returned blobs under debug.
- Implements initialization and cleanup:
  - `init_cifs_spnego()` creates kernel credentials, allocates a private `.cifs_spnego` thread keyring, registers the key type, and configures request-key caching.
  - `exit_cifs_spnego()` revokes the keyring, unregisters the key type, and releases credentials.

## Key Data/Control Flow

- The private `spnego_cred` is both a request credential and a gate: only code executing with it can create valid `cifs.spnego` keys.
- The key description is treated as authority-bearing input to userspace `cifs.upcall`.
- Upcall target is explicitly encoded as `mount` or `app`.
- Returned key payload is expected to contain `struct cifs_spnego_msg` from `cifs_spnego.h`.

## Security Notes

- `vet_description` prevents arbitrary userspace `add_key()`/`request_key()` from injecting privileged CIFS SPNEGO descriptions.
- The request keyring is root-owned, root-clearable, and not quota-accounted.
- Debug blob dumping can expose authentication material when extra debugging is enabled.
