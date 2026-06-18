<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/selinux/libselinux/src/validatetrans.c -->
# sources/security-integrity/selinux/libselinux/src/validatetrans.c

## Purpose
Asks the kernel whether a source, target, class, and new context transition is valid under policy constraints.

## Important APIs, Types, And Functions
`security_validatetrans_raw()` writes a space-separated query to `<selinux_mnt>/validatetrans`. `security_validatetrans()` translates all contexts to raw form before calling the raw helper.

## Control Flow
The raw helper allocates one page, formats `scon tcon class newcon`, rejects truncation, writes to the control file, and converts positive byte-count success to `0`.

## State And Persistence Behavior
The kernel validates the transition; no persistent policy or label state is changed.

## Dependencies And Integration Points
Depends on context translation, class unmapping, selinuxfs, and `selinux_page_size`. The utility `validatetrans` wraps this API.

## Risks And Test Signals
Risks include contexts containing spaces, page-size truncation, class mapping errors, and write return semantics. Tests should cover valid/invalid transitions, translated contexts, unset selinuxfs, very long contexts, and invalid classes.
<!-- END_FILE_RESEARCH: sources/security-integrity/selinux/libselinux/src/validatetrans.c -->
