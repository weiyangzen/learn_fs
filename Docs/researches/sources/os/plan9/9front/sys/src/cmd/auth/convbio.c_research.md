# File Research: sources/os/plan9/9front/sys/src/cmd/auth/convbio.c

Account bio format converter.

Key responsibilities:
- Reads legacy whitespace/angle-bracket account bio lines from stdin.
- Parses user, name, department, and up to `Nemail` email addresses.
- Writes normalized pipe-delimited records containing user, post id, name, department, and emails.
- Clears/reuses `Acctbio` storage for each input record.

Dependencies:
- Uses `Acctbio` and constants from `authcmdlib.h`.

Research notes:
- If no email is present, output defaults the first email field to the username.
- The parser returns one account per successful `ordbio()` call.
