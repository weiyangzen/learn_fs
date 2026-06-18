# sources/user-network-fs/smblibrary/SMBServer/UserCollection.cs

Purpose: `UserCollection` extends `List<User>` with SMB account-specific lookup helpers.

Important APIs/types/functions: `Add(string,string)` creates a `User`; `IndexOf(string)` performs case-insensitive account lookup; `GetUserPassword(string)` returns the stored password or null; `ListUsers()` returns account names in list order.

Control flow: lookups linearly scan the list and compare `AccountName` using `StringComparison.OrdinalIgnoreCase`. Password lookup delegates to `IndexOf`.

State and persistence behavior: all state is inherited mutable list state. There is no duplicate enforcement, so the first case-insensitive match wins.

Dependencies and integration points: populated by `SettingsHelper` and likely consulted by authentication code.

Risks: linear lookup can be fine for small config files but scales poorly. Duplicate user names, null `AccountName`, and plaintext password handling are not guarded. Inheriting from `List<User>` exposes arbitrary mutation that can bypass helper semantics.

Test signals: useful tests include case-insensitive lookup, duplicate handling, null account behavior, empty collection lookup, and order preservation in `ListUsers()`.
