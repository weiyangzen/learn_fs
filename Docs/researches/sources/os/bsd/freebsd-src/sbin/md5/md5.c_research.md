# File Research: sources/os/bsd/freebsd-src/sbin/md5/md5.c

## Purpose
Implements FreeBSD’s multi-algorithm checksum utility, supporting BSD-style digest commands, GNU `*sum` compatibility, and partial Perl `shasum` compatibility.

## Main Responsibilities
- Selects digest algorithm based on executable name or `shasum -a`.
- Supports MD5, SHA1, SHA224, SHA256, SHA384, SHA512, SHA512/224, SHA512/256, RIPEMD160, Skein256, Skein512, and Skein1024.
- Reads files, stdin, or strings and emits checksums in several output formats.
- Verifies checksum files in BSD/GNU/Perl-compatible modes.
- Provides self-test vectors and a time trial benchmark.
- Optionally uses Capsicum/Casper fileargs for sandboxed file opening.

## Key Implementation Details
- `Algorithm[]` maps executable/program names to digest init/update/end/data functions and expected test output tables.
- Mode is inferred from `progname`:
  - `mode_bsd` for names like `md5`, `sha256`.
  - `mode_gnu` for names ending in `sum`.
  - `mode_perl` for `shasum`.
- Input modes:
  - binary
  - text
  - universal newline normalization
  - bit-string mode
- Output modes:
  - bare digest
  - tagged BSD format
  - reverse format
  - GNU format
- `gnu_check()` parses checksum files in both BSD tagged format and GNU format, building a linked list of checksum records.
- `MDInput()` streams data in 4096-byte blocks, optionally teeing stdin to stdout for passthrough mode.
- Universal mode normalizes CR/CRLF to LF before hashing.
- Bit input mode packs ASCII `0`/`1` characters into bytes and rejects non-byte-aligned input.
- `MDOutput()` handles normal printing and check-result reporting, including quiet/status behavior.
- `MDTimeTrial()` hashes a large fixed block workload and reports speed.
- `MDTestSuite()` hashes built-in vectors and marks failures.
- `safename()` uses `vis(3)` escaping before printing filenames.

## Command-Line Behavior
BSD-style options include:
- `-c string`
- `-p`
- `-q`
- `-r`
- `-s string`
- `-t`
- `-x`

GNU/Perl-style options include:
- `--check`
- `--ignore-missing`
- `--quiet`
- `--status`
- `--strict`
- `--tag`
- `--text`
- `--binary`
- `--warn`
- `--zero`
- `--version`

Perl-style adds:
- `-a`/`--algorithm`
- `-0`/`--01`
- `-U`/`--UNIVERSAL`

## Security/Capability Behavior
When built with Capsicum:
- Limits stdio rights early.
- Initializes fileargs with read/fstat/fcntl rights.
- Enters capability mode before opening input files through Casper.

## Notable Edge Cases
- GNU check mode rewrites `argv` to filenames parsed from checksum records.
- `ignoreMissing` suppresses missing-file failures only in checksum mode.
- BSD `-b` is a no-op for compatibility.
- In GNU mode, output defaults to true GNU format rather than historical FreeBSD reverse behavior.
- Exit code is `1` for operational failure or strict malformed checksum input, and `2` when checksums fail after successful processing.
