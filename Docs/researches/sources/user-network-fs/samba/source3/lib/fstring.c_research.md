# sources/user-network-fs/samba/source3/lib/fstring.c

Purpose: supplies fixed-size ASCII conversion helpers for source3 `fstring` and NetBIOS `nstring` buffers.

Important APIs/types/functions: `push_ascii_fstring()`, `pull_ascii_fstring()`, `push_ascii_nstring()`, and `pull_ascii_nstring()`.

Control flow: fstring helpers delegate to bounded `push_ascii()`/`pull_ascii()`. Nstring push uses `convert_string_error(CH_UNIX, CH_DOS, ...)`, NUL-terminates on success or truncation, and clears the destination on hard failure. Nstring pull allows DOS-to-Unix expansion into a caller-sized buffer.

State/persistence behavior: no global state; key behavior is bounds and NUL-termination handling for stack/struct buffers.

Dependencies/integration: used throughout source3 code that still relies on `fstring`.

Risks/test signals: truncation, conversion failure, and guaranteed NUL termination are the main risks. Tests should cover oversized and unconvertible strings.
