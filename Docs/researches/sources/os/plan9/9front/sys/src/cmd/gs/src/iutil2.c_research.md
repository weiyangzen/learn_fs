# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/iutil2.c

Implements Level 2 password utility routines. Parameter-list helpers can read passwords as strings or integer values, write passwords back as strings, and compare a supplied `"Password"` parameter against a stored password.

Dictionary helpers locate password strings in dictionaries, read the length-prefixed stored password form, and write a new password when allowed. Access and range checks protect against malformed password storage, oversized values, and unauthorized password changes.

The file depends on parameter-list APIs, dictionary lookup, byte comparison, and interpreter error conventions.
