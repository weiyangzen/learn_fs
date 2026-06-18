# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/iutil2.c

Purpose: implements Level 2 interpreter password utilities.

Functions:
- `param_read_password` reads a password from a parameter list as a string, or accepts an integer by converting it to decimal text after an initial typecheck.
- `param_write_password` writes password bytes to a parameter list.
- `param_check_password` compares a supplied `Password` parameter against a configured password.
- `dict_read_password` and `dict_write_password` read/write encoded password strings in dictionaries, using a first-byte length convention and optional change authorization.

Important validation: password size is capped by `MAX_PASSWORD`; dictionary password storage must be a string without read access and with a valid embedded length byte.
