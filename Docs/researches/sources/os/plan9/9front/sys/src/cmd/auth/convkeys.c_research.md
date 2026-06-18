# File Research: sources/os/plan9/9front/sys/src/cmd/auth/convkeys.c

Key database re-encryption and migration tool for Plan 9 auth key files.

Key responsibilities:
- Reads an encrypted key database into memory and decrypts it with either NVRAM machine key or an entered password.
- Recognizes legacy DES format and AES format with `"AES KEYS"` header.
- Validates fixed-size records by checking user names as UTF.
- In verbose mode, prints decrypted usernames without re-encrypting.
- Re-encrypts the database with a newly entered key.
- Optionally converts legacy DES records to AES-format records, appending zeroed AES-key fields.

Dependencies:
- Uses `Authkey`, key database constants, `getauthkey`, `getpass`, `private`, DES/AES CBC routines, and Plan 9 auth command helpers.

Notable risks:
- Operates in place on the key file after successful conversion.
- AES conversion requires an AES machine key; old NVRAM without AES material aborts conversion.
