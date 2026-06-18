# File Research: sources/os/bsd/netbsd-src/lib/libcrypt/bcrypt.c

Read completely: 376 lines.

Implements bcrypt password hashing and bcrypt salt generation. It includes `blowfish.c` directly, then uses EksBlowfish setup: initialize Blowfish state, expand with salt and password, repeat key expansion for `2^log_rounds`, encrypt the fixed ciphertext `OrpheanBeholderScryDoubt` 64 times, and encode salt plus ciphertext in bcrypt’s custom base64 alphabet.

`__gensalt_blowfish()` parses the log-round option, clamps it to 4..31, generates 16 random salt bytes with `arc4random()`, and emits `$2a$NN$...`. `bcrypt_gensalt()` is a compatibility wrapper returning a static salt buffer.

`__bcrypt()` validates `$2a$`-style salts, decodes 16 salt bytes, caps passwords at 72 bytes, includes the NUL terminator for minor version `a`, and returns a static `_PASSWORD_LEN` buffer. The function scrubs the Blowfish state before returning, but the static output buffer makes the API non-thread-safe in the traditional `crypt(3)` style.
