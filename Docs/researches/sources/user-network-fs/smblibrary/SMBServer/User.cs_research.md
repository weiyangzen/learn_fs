# sources/user-network-fs/smblibrary/SMBServer/User.cs

Purpose: `User` is the SMBServer account record used by `UserCollection`.

Important APIs/types/functions: public fields `AccountName` and `Password`; the constructor assigns both.

Control flow: no internal branching. It is constructed by `UserCollection.Add(accountName, password)` and by settings loading.

State and persistence behavior: in-memory plaintext credentials only; no hashing, expiration, or secure storage semantics.

Dependencies and integration points: used by `UserCollection` and populated from `SettingsHelper.ReadUserSettings()`.

Risks: public mutable plaintext password field is the main security and integrity risk. Null or duplicate account names are not rejected at this layer.

Test signals: tests should exercise construction, null/empty values if allowed by callers, and password lookup through `UserCollection`.
