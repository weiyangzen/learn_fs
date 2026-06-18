# File Research: sources/os/linux/linux-stable/fs/smb/client/unc.c

## Summary
Provides small UNC parsing helpers for the SMB client.

## Main Interfaces
- `extract_hostname(const char *unc)`: validates a UNC-like string, skips leading backslashes, finds the next backslash delimiter, allocates and returns the hostname portion.
- `extract_sharename(const char *unc)`: skips the initial two characters, finds the share-name delimiter, and duplicates the remainder as the share name.

## Behavior
Both functions return allocated strings on success and `ERR_PTR()` on failure. `extract_hostname()` checks minimum length, rejects all-backslash strings, requires a hostname/share delimiter, and returns `-EINVAL` or `-ENOMEM`. `extract_sharename()` assumes a conventional leading `\\`, requires the next `\`, duplicates the share substring, and returns `-EINVAL` or `-ENOMEM`.

## Dependencies And Risks
The code depends on callers passing normalized UNC strings using backslash delimiters. `extract_sharename()` performs less validation than `extract_hostname()` and directly starts at `unc + 2`, so malformed short strings must be filtered by callers or earlier normalization.
