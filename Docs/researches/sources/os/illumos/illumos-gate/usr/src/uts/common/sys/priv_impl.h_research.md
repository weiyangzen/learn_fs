# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/priv_impl.h

## Purpose
Defines the kernel-private privilege-set storage layout, credential privilege container, fast privilege bit operations, and internal privilege-set globals.

## Main Interfaces
- `struct priv_set`: array of `PRIV_SETSIZE` `priv_chunk_t` words.
- `cred_priv_t`: per-credential privilege sets plus credential privilege flags.
- Globals:
  - `priv_basic`
  - `priv_unsafe`
  - `priv_fullset`
- `priv_init()`
- Credential privilege access macros:
  - `CR_EPRIV`
  - `CR_IPRIV`
  - `CR_PPRIV`
  - `CR_LPRIV`
  - `CR_FLAGS`
  - `CR_OEPRIV`
  - `CR_OPPRIV`
- Awareness/validation:
  - `PRIV_EISAWARE`
  - `PRIV_PISAWARE`
  - `PRIV_VALIDSET`
  - `PRIV_VALIDOP`
  - `PRIV_FULLSET`
- Bit layout and operations:
  - `PRIV_SETBYTES`
  - `__NBWRD`
  - `privmask()`
  - `privword()`
  - `PRIV_ASSERT`
  - `PRIV_CLEAR`
  - `PRIV_ISASSERT`

## Dependencies And Relationships
Includes `sys/priv_const.h` and `sys/priv.h`. Relies on `CR_PRIVS()` from `sys/cred_impl.h`.

## Research Notes
Debug kernels route bit operations through checked helper functions; non-debug kernels use direct bit manipulation. Bit numbering is arranged through `privmask()` using high-bit-first placement within each word.
