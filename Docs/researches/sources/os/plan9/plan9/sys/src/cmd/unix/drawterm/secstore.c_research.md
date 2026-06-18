# File Research: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/secstore.c

Compact drawterm copy of secstore client code, enough to check for and fetch a boot-time `factotum` file.

Major pieces:
- `secdial` resolves `$auth`/authserver naming and dials TCP port 5356.
- `havesecstore` sends a minimal secstore PAK probe and interprets account-existence responses.
- `SConn`/`SS` implement a delimited connection that can switch to SHA1/RC4 authenticated encryption using `SC_secret`, `SC_read`, and `SC_write`.
- `getfile` requests `GET factotum`, receives encrypted file chunks, derives an AES-CBC key from the password, decrypts, and verifies the trailing `XXXXXXXXXXXXXXXX` check block.
- PAK support includes fixed group parameters, `longhash`, `PAK_Hi`, `shorthash`, and `PAKclient`.
- `secstorefetch` prompts or accepts a password, performs PAK, handles optional STA/SecurID challenge, fetches and decrypts the file, sends `BYE`, and returns the file contents.

Important dependencies:
- Plan 9 networking/dialing, mpint arithmetic, SHA1/HMAC, RC4, AES-CBC, `readcons`, and drawterm globals such as `authserver`.

Notable behavior and risks:
- Max fetched file size is capped at 10 MiB.
- The encrypted channel uses legacy RC4/SHA1 after PAK.
- The secstore file encryption path uses AES-CBC plus a fixed check trailer.
- `emalloc` is `mallocz` without explicit failure handling in this file.
