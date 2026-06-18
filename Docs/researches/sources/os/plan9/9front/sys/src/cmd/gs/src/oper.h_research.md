# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/oper.h

Central Ghostscript interpreter operator header. It defines the operator procedure convention, pulls in operand stack, operator definition, external operator declaration, operand checking, and utility headers, and supplies common checking macros used by `z*` operator implementations.

The key logic is type-check error handling: bottom operand-stack guard slots use invalid refs, so failed type checks call `check_type_failed` to distinguish `typecheck` from `stackunderflow`. The header also defines access/type check macros and positive operator return codes for execution-stack push/pop and Display PostScript rescheduling.

Dependencies include `ierrors.h`, `ostack.h`, `opdef.h`, `opextern.h`, `opcheck.h`, `iutil.h`, and the interpreter context model.

This file is core Ghostscript interpreter infrastructure and has no direct filesystem role.
