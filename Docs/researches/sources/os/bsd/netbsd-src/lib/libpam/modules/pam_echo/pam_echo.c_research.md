# File Research: sources/os/bsd/netbsd-src/lib/libpam/modules/pam_echo/pam_echo.c

PAM module that emits configured messages through `pam_info`. `_pam_echo` concatenates module arguments into a bounded PAM message, expanding `%H`, `%s`, `%t`, `%U`, and `%u` from PAM items; `%h` is intentionally not implemented.

Authentication, account, open session, close session, and committed password-change phases emit the message. Setcred succeeds silently, and password preliminary check succeeds without output.
