# sources/user-network-fs/samba/source3/rpc_client/init_samr.c

## Purpose
`init_samr.c` builds encrypted SAMR password buffers for password-change and account-management RPC calls. It supports legacy RC4 formats and the AES/HMAC-SHA512 encrypted password structure.

## Important APIs, Types, And Functions
Exports are `init_samr_CryptPasswordEx()`, `init_samr_CryptPassword()`, and `init_samr_CryptPasswordAES()`. They populate `samr_CryptPasswordEx`, `samr_CryptPassword`, and `samr_EncryptedPasswordAES`. The file uses `encode_rc4_passwd_buffer()`, `encode_pw_buffer()`, `encode_pwd_buffer514_from_str()`, GnuTLS ARCFOUR, and Samba AEAD helpers with SAMR-specific salts.

## Control Flow
`init_samr_CryptPasswordEx()` delegates directly to `encode_rc4_passwd_buffer()`. `init_samr_CryptPassword()` encodes a 516-byte Unicode password buffer, initializes an ARCFOUR cipher from the session key, encrypts the fixed-size buffer, and maps GnuTLS failures to NTSTATUS. `init_samr_CryptPasswordAES()` validates the output pointer, encodes a 514-byte plaintext password buffer, encrypts it with AES-256-CBC/HMAC-SHA512 using the supplied salt and session key, wipes the stack plaintext with `BURN_DATA()`, copies the salt into the output, sets ciphertext length/data, and leaves `PBKDF2Iterations` as zero.

## State And Persistence
The file does not persist state. It writes caller-supplied output structs and talloc-allocated ciphertext. Sensitive plaintext is stack-local in the AES path and explicitly burned; the RC4 paths rely on helper behavior and output buffers.

## Dependencies And Integration Points
Dependencies include libcli auth password encoders, generated SAMR RPC types, GnuTLS, and Samba crypto helper salts. Callers include `rpcclient/cmd_samr.c`, join/password-change code, NetAPI user code, source4 libnet password code, and SAMR torture tests.

## Risks
Session key and salt sizes are assumed to match protocol expectations; the AES path asserts salt length matches the output struct. RC4 remains required for older protocol compatibility but is cryptographically legacy. The fixed buffer sizes are protocol-specific and must not be changed casually. `init_samr_CryptPasswordEx()` relies entirely on delegated error handling.

## Test Signals
SAMR torture tests exercise password set/change paths with RC4 and AES. Additional signals include invalid output pointer handling, malformed salt length assertions in debug builds, GnuTLS failure mapping, and server-side acceptance of generated password buffers in join, rpcclient, and NetAPI flows.
