# File Research: sources/os/bsd/freebsd-src/sbin/setkey/scriptdump.pl

## Summary
Perl helper that converts `setkey -D` SAD dump output back into `setkey` add/delete script commands.

## Main Elements
- Requires root by checking effective UID.
- Accepts optional `-d` to emit `delete` commands instead of `add`.
- Reads `setkey -D` output from a pipe.
- Captures source/destination, protocol, mode, SPI, reqid, replay, encryption algorithm/key, and authentication algorithm/key.
- Emits semicolon-terminated setkey commands.

## Dependencies And Integration
Depends on stable text formatting from `setkey -D`; intended to be generated with the configured local Perl prefix.
