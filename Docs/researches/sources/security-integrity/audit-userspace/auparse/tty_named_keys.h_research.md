<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/audit-userspace/auparse/tty_named_keys.h -->
# sources/security-integrity/audit-userspace/auparse/tty_named_keys.h

Purpose: macro-expanded lookup data mapping terminal byte sequences to human-readable key names for TTY audit data interpretation.

Important APIs and types: the file defines no functions itself; consumers supply macro `E(sequence, name)` before including it. Entries cover control characters, delete/backspace, tab/newline/return, escape, CSI/SS3 function keys, cursor keys, page/home/end/insert/delete, shifted variants, mouse sequences, and keypad aliases.

Control flow and state: none at runtime in this header. Ordering is semantic data: comments state longest sequences should precede shorter ones so consumers can match escape prefixes without prematurely selecting `esc` or shorter CSI aliases.

Dependencies and integration: based on terminal descriptions from ncurses-era data and consumed by auparse TTY interpretation code. It has no include guards because repeated macro inclusion is intentional.

Risks and test signals: risks include ambiguous terminal sequences, alias choices documented in comments, and the need to keep `E("\x1B", "esc")` after longer escape sequences. Test coverage is indirect through TTY interpretation output and any parser golden files that include TTY data.
<!-- END_FILE_RESEARCH: sources/security-integrity/audit-userspace/auparse/tty_named_keys.h -->
