# File Research: sources/os/plan9/plan9/sys/src/cmd/auth/printnetkey.c

Prints the network key for a named user from `NETKEYDB`. It validates the username fits `ANAMELEN`, reads the key file, and formats it with `%K`.

Intended for auth administrators inspecting network access keys.
