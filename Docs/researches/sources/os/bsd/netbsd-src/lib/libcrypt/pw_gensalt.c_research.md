# File Research: sources/os/bsd/netbsd-src/lib/libcrypt/pw_gensalt.c

Read completely: 300 lines.

Implements `pw_gensalt()`, dispatching named salt types to scheme-specific generators: `old`, `new`/`newsalt`, `md5`, `sha1`, `blowfish`, and optional Argon2 variants. It returns `EINVAL` for unknown types.

The DES generators emit two-character traditional salts or extended DES salts with clamped rounds from 7250 to `0xffffff`. MD5 emits `$1$` plus eight random crypt-base64 characters. SHA1 emits `$sha1$<randomized iterations>$<8 random chars>$`. Blowfish delegates to `__gensalt_blowfish()`.

When Argon2 is enabled, option parsing accepts `m=`, `t=`, and `p=`, fills missing/too-small values with `estimate_argon2_params()`, emits ordered `$argon2*$v=<version>$m=...,t=...,p=...$`, then appends 16 random standard-base64 characters and a trailing `$`. Some buffer-too-small paths return `0` without setting `errno`, reflecting historical API looseness.
