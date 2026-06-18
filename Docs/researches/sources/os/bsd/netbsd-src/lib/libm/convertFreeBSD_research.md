# File Research: sources/os/bsd/netbsd-src/lib/libm/convertFreeBSD

## Scope

Small shell script for mechanical conversion of FreeBSD libm source identifiers to NetBSD naming/layout conventions.

## APIs And Behavior

- Runs `sed -i` on supplied files.
- Rewrites `IEEEl2bits` to `ieee_ext_u`.
- Rewrites long-double bit-field references such as `bits.man`, `bits.exp`, `bits.sign`, and `.e` to NetBSD names.
- Rewrites `LDBL_MANH_SIZE` / `LDBL_MANL_SIZE` to `EXT_FRACHBITS` / `EXT_FRACLBITS`.
- Rewrites `u.xbits.expsign` to `GET_EXPSIGN(&u)`.

## Dependencies And Risks

- In-place script; intended for source import/conversion, not runtime.
- Pattern substitutions are mechanical and can affect unintended matching text if used broadly.
