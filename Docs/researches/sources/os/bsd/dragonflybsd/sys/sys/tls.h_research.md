# File Research: sources/os/bsd/dragonflybsd/sys/sys/tls.h

Thread-local storage syscall ABI.

Key contents:
- Defines `struct tls_info`:
  - base pointer
  - signed size
- Declares:
  - `set_tls_area`
  - `get_tls_area`
- On x86_64, defines selectors:
  - `TLS_WHICH_FS`
  - `TLS_WHICH_GS`

Important behavior:
- `size` is explicitly signed.
- APIs take an `infosize` argument for structure-size/version checking.

Research notes:
- This is small user/kernel ABI for architecture TLS register areas.
- The x86_64 definitions map TLS selection to FS/GS.
