# File Research: sources/os/bsd/freebsd-src/sbin/veriexec/manifest_parser.y

## Purpose
Yacc parser for Veriexec manifest lines, converting path/fingerprint/flag records into kernel Veriexec load ioctls.

## Main Elements
- Grammar parses `path attributes eol`, recovering by skipping to the next fingerprint on parse errors.
- Attributes include hash fields (`sha1`, `sha256`, `sha384`, `sha512`), `label`, and octal `mode`.
- Flags include `indirect`, `no_ptrace`, `trusted`, and optionally `no_fips`.
- Relative manifest paths are converted to absolute paths, optionally prefixed by `Cdir`.
- `convert()` transforms fixed-length hex fingerprints into binary digests.
- `do_ioctl()` classifies non-executable paths as `VERIEXEC_FILE`, applies forced flags, and sends `VERIEXEC_SIGNED_LOAD` or label load ioctls.
- `manifest_parser_init()` invalidates the current fingerprint state between manifests.

## Dependencies And Integration
Uses Veriexec ioctl ABI, libsecureboot digest size definitions, BearSSL digest constants fallback, optional label support, and globals from `veriexec.c`.

## Risk Notes
Fingerprint conversion assumes the input string is long enough for the declared digest size. Missing fingerprint type causes a manifest entry to be skipped.
