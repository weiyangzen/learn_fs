# File Research: sources/os/plan9/9front/sys/src/cmd/auth/secstore/secstore.c

Client for Plan 9 `secstore`, a network-backed private file store. It authenticates to `secstored` using PAK over `SConn`, then issues textual protocol commands: `GET`, `PUT`, `RM`, `CHPASS`, and `BYE`.

Important behavior:
- `getfile()` requests a file, handles directory listing via `GET .`, and decrypts stored files using AES-CBC. The AES key is SHA1 over `"aescbc file"` plus the user passphrase, and the file contains an IV plus a trailing 16-byte `"XXXXXXXXXXXXXXXX"` check marker.
- `putfile()` encrypts local or in-memory data with a fresh IV and sends encrypted length plus encrypted chunks to the server.
- `cmd()` executes all requested gets, puts, and removes on one authenticated connection.
- `chpasswd()` changes the server-side PAK verifier, downloads every stored file, decrypts with the old passphrase, and reuploads encrypted with the new passphrase.
- `login()` supports passphrase from console, stdin, or NVRAM, tries one or more destinations, handles optional STA PIN+SecureID challenge, and stores passphrase length for file encryption.

Interfaces/dependencies:
- Uses `SConn`, `readstr`, `writerr`, `PAKclient`, and `PAK_Hi`.
- Default server is `$auth` unless `-s` or `$secstore` supplies destinations.
- File payload security is client-side; the server stores encrypted bytes but knows filenames and lengths.

Risks/notes:
- The file-authentication check is only a fixed plaintext marker after decryption, not a MAC.
- Password change is explicitly vulnerable to connection failure because it rekeys files sequentially after changing the verifier.
