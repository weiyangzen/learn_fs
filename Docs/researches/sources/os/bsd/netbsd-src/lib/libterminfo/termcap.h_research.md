# File Research: sources/os/bsd/netbsd-src/lib/libterminfo/termcap.h

Public termcap compatibility header.

Key contents:
- Declares output functions shared with terminfo:
  - `putp`
  - `tputs`
- Declares global compatibility variables:
  - `ospeed`
  - `PC`
  - `BC`
  - `UP`
- Declares classic termcap APIs:
  - `tgetent`
  - `tgetstr`
  - `tgetflag`
  - `tgetnum`
  - `tgoto`

Role in subsystem:
- Public ABI for applications expecting historical termcap interfaces.
