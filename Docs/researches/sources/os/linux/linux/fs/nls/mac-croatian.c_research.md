# File Research: sources/os/linux/linux/fs/nls/mac-croatian.c

Implements the `maccroatian` NLS codepage module.

Main structure:
- Generated Mac Croatian translation tables.
- `charset2uni[256]` includes base Mac Roman-like entries plus Croatian-specific characters such as Latin Extended forms and an Apple private-use mapping.
- Reverse Unicode-to-charset pages include `0x00`, `0x01`, `0x02`, `0x03`, `0x20`, `0x21`, `0x22`, `0x25`, and `0xf8`.
- Includes `charset2lower[256]` and `charset2upper[256]` sentinel tables.
- `uni2char()` and `char2uni()` follow the common single-byte NLS implementation pattern.
- Registers as charset `maccroatian`.

Lifecycle:
- `init_nls_maccroatian()` registers the NLS table.
- `exit_nls_maccroatian()` unregisters it.
- Module description is `NLS Codepage maccroatian`; license is `Dual BSD/GPL`.

Risk notes:
- The reverse table includes private-use page `0xf8`, so compatibility with non-Apple Unicode expectations depends on preserving that exact mapping.
