# File Research: sources/os/bsd/netbsd-src/lib/libterminfo/term.h

Public terminfo API and capability macro header.

Key contents:
- Defines `ERR` and `OK` if absent.
- Enumerates all supported terminfo capability IDs:
  - `enum TIFLAGS`
  - `enum TINUMS`
  - `enum TISTRS`
- Defines `TIFLAGMAX`, `TINUMMAX`, and `TISTRMAX`.
- Provides `t_*` macros for explicit `TERMINAL *` access.
- Provides traditional global macros using `cur_term`.
- Documents boolean, numeric, and string capability meanings in comments.
- Defines public `TERMINAL` shape when `_TERMINFO` is not already set.
- Declares standard and NetBSD extension APIs:
  - `setupterm`
  - `set_curterm`
  - `del_curterm`
  - `termname`
  - `longname`
  - `tigetflag`
  - `tigetnum`
  - `tigetstr`
  - `tparm`
  - `ti_setupterm`
  - `ti_getflag`
  - `ti_getnum`
  - `ti_getstr`
  - `ti_parm`
  - `ti_puts`
  - `ti_putp`
  - `tiparm`
  - `ti_tiparm`
  - optional `tlparm`
  - `captoinfo`
- Includes `termcap.h` as required by POSIX behavior noted in the file.

Role in subsystem:
- Primary public contract for applications using NetBSD `libterminfo`.
