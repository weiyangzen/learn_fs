# sources/user-network-fs/smblibrary/SMBServer/ShareSettings.cs

Purpose: `ShareSettings` is a simple mutable data carrier for one SMB share definition.

Important APIs/types/functions: public fields `ShareName`, `SharePath`, `ReadAccess`, and `WriteAccess`; the constructor assigns all four values directly.

Control flow: there is no logic beyond construction. Instances are produced by `SettingsHelper.ReadSharesSettings()` and later consumed by server/share setup code.

State and persistence behavior: stores in-memory configuration only. The access lists are held by reference, not copied, so external mutations of the lists affect the instance.

Dependencies and integration points: depends on `System.Collections.Generic.List<string>` and is integrated with `SettingsHelper`.

Risks: public mutable fields allow uncontrolled changes and null values. No validation enforces a non-empty share name, valid path, or normalized access principals.

Test signals: tests should assert constructor assignment and downstream behavior when read/write lists are empty, wildcard-derived, or mutated after construction.
