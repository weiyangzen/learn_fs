# sources/security-integrity/selinux/libsemanage/src/utilities.h

## Purpose
Declares libsemanage utility helpers and the `semanage_list_t` string-list type.

## APIs and integration
Exposes parsing helpers, list operations, string counting/trimming/replacement, whitespace truncation, filtered slurp, `write_full()`, and portable `semanage_basename()`. `WARN_UNUSED` annotates functions where ignoring failures is risky.

## State and risks
The list type owns `data` strings for normal push/pop/destroy flows, but `semanage_slurp_file_filter()` deliberately transfers getline buffers into list nodes. Callers must free returned strings/lists according to the producing API.
