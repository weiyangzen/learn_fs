# File Research: sources/os/bsd/freebsd-src/sbin/devd/parse.y

## Purpose
Yacc grammar for `devd.conf` files.

## Main Elements
- Supports `options`, `attach`, `detach`, `nomatch`, and `notify` blocks.
- Option statements: `directory`, `pid-file`, and `set`.
- Event statements: `match`, shorthand `device-name`, `media-type`, `class`, `subdevice`, and `action`.
- Semantic actions call C-compatible constructors declared in `devd.h`.

## Dependencies And Integration
Generated parser is built into `devd`. Tokens are produced by `token.l`; runtime objects are created in `devd.cc`.

## Risk Notes
Empty event blocks are allowed by grammar but do not add event processors.
