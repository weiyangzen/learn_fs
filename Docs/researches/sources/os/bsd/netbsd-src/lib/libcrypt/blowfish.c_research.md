# File Research: sources/os/bsd/netbsd-src/lib/libcrypt/blowfish.c

Read completely: 495 lines.

Contains the trimmed Blowfish block cipher implementation used only by `bcrypt.c`; it is included directly rather than built as an independent object. It defines `blf_ctx` with four 256-entry S-boxes and eighteen P-subkeys initialized from the standard Blowfish Pi-derived constants.

Implemented helpers include `Blowfish_encipher()`, `Blowfish_initstate()`, `Blowfish_stream2word()`, `Blowfish_expand0state()`, `Blowfish_expandstate()`, and `blf_enc()`. These are exactly the bcrypt-needed operations: initialize state, fold in key material and salt, expand P/S arrays, and encrypt 64-bit block pairs.

The file is crypto core code with no external API boundary in this library. Risks are mostly integration-related: it assumes bcrypt’s byte order and key-stream cycling behavior, and its static functions rely on being included into `bcrypt.c`.
