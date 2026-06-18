# File Research: sources/os/plan9/9front/sys/src/cmd/auth/factotum/totp.c

Factotum TOTP/HOTP one-time password generator.

Key responsibilities:
- Finds a key with private base32 `!secret`.
- Supports optional public `digits` and `period` attributes.
- Decodes the secret, computes HOTP with HMAC-SHA1 dynamic truncation, and derives TOTP from current nanosecond time.
- Returns a zero-padded code with default 6 digits and 30-second period.
- Rejects invalid digit counts and non-positive periods.

Dependencies:
- Uses factotum key lookup, base32 decode, HMAC-SHA1, and `nsec`.

Notable risks:
- Maximum generated code length is 8 digits.
