# File Research: sources/os/bsd/freebsd-src/sbin/md5/Makefile

## Purpose
Builds the multi-algorithm digest utility installed as `md5` and many hard-linked command aliases.

## Main Responsibilities
- Builds `PROG=md5`.
- Creates links for MD5, RIPEMD160, SHA variants, and Skein variants, including GNU-style `*sum` names.
- Installs matching manual-page links.
- Links against `libmd`.
- Optionally enables Capsicum/Casper fileargs support when available and not bootstrapping.
- Adds tests subdirectory when tests are enabled.

## Supported Aliases
Includes:
- `md5`, `md5sum`
- `rmd160`, `rmd160sum`
- `sha1`, `sha1sum`
- `sha224`, `sha224sum`
- `sha256`, `sha256sum`
- `sha384`, `sha384sum`
- `sha512`, `sha512sum`
- `sha512t224`, `sha512t224sum`
- `sha512t256`, `sha512t256sum`
- `skein256`, `skein256sum`
- `skein512`, `skein512sum`
- `skein1024`, `skein1024sum`

## Notable Build Detail
`shasum` compatibility links are documented but commented out.
