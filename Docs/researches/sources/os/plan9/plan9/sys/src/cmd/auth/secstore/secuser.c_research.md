# File Research: sources/os/plan9/plan9/sys/src/cmd/auth/secstore/secuser.c

Interactive secstore account administration tool. It ensures secstore directories exist, creates or edits a `PW` account, prompts for password, expiration date, enabled/disabled state, STA requirement, and comments.

New passwords are converted to `PAK-Hi`; existing accounts can keep their current password by entering an empty password. New accounts also create `/adm/secstore/store/<user>`.

Writes changes through `putPW` and logs `CHANGELOGIN`.
