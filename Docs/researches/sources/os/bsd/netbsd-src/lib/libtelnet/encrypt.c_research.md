# File Research: sources/os/bsd/netbsd-src/lib/libtelnet/encrypt.c

## Purpose
Implements Telnet ENCRYPT option negotiation, command handling, key-id exchange, and activation of selected encryption/decryption methods.

## Main Interfaces
Exports global function pointers `encrypt_output` and `decrypt_input`, encryption command handlers, support/is/reply/start/end/keyid handlers, session-key distribution, auto mode controls, wait logic, and printsub helpers.

## Control Flow And State
The `encryptions[]` table currently contains DES_CFB64 and DES_OFB64 when DES encryption is compiled. Global masks track local support, disabled support, and remote support for each direction. Additional globals track current encrypt/decrypt modes, verbosity/debug flags, autoencrypt/autodecrypt, session-key availability, role, and display name.

`encrypt_init` resets negotiation state, builds an ENCRYPT SUPPORT suboption listing enabled decryption types, and initializes each backend. Command functions enable/disable/type/start/stop input and output directions, using `genget` for type lookup.

`encrypt_support` records remote decrypt capabilities and selects a usable output encryption type. `encrypt_is` and `encrypt_reply` dispatch initial method negotiation to backend hooks and optionally auto-start. `encrypt_start` installs the active decrypt input callback after receiving ENCRYPT START.

Key-id handling keeps separate direction records, calls backend key-id validators, and sends escaped key-id suboptions. `encrypt_start_output` emits ENCRYPT START, calls `net_encrypt` to flush/ring-encrypt correctly, then installs the output encrypt callback. `encrypt_send_end` clears output encryption after emitting ENCRYPT END.

## Dependencies
Uses telnet ENCRYPT constants, DES backends, generic command lookup from `misc.h`, and application-provided `telnet_net_write`, `net_encrypt`, `telnet_spin`, and `printsub`.

## Risks And Notes
State is global, not per connection. Auto-start behavior depends on session key arrival and remote support masks. Output mode switches are sensitive to telnet ring ordering: the code intentionally encrypts pending output in the old mode before installing the new callback.
