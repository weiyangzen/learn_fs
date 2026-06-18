# File Research: sources/os/plan9/plan9/sys/src/cmd/auth/netkey.c

Interactive netkey response generator. It refuses to run on CPU servers, prompts for a password, derives a DES key with `passtokey`, then loops reading numeric challenges from stdin and printing encrypted responses.

Uses `netcrypt` to produce the response string.
