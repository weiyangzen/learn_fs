# sources/user-network-fs/smblibrary/SMBServer/SettingsHelper.cs

Purpose: `SettingsHelper` is the SMBServer configuration loader for `Settings.xml` beside the Windows Forms executable. It converts XML user and share definitions into `UserCollection` and `List<ShareSettings>` instances consumed by the SMB server sample.

Important APIs/types/functions: `SettingsFileName` fixes the expected file name; `ReadXmlDocument(path)` loads an `XmlDocument`; `ReadSettingsXML()` derives the executable directory through `Application.ExecutablePath`; `ReadUserSettings()` reads `Settings/Users` child nodes and creates users from `AccountName` and `Password`; `ReadSharesSettings()` reads `Settings/Shares`, share `Name`/`Path`, and nested `ReadAccess`/`WriteAccess`; `ReadAccessList(XmlNode)` maps `Accounts="*"` to the local group string `Users` or splits comma-separated account names.

Control flow: callers request users or shares, the helper loads the XML fresh each time, selects the relevant top-level node, iterates children, extracts attributes without optional checks, and populates DTO containers. Access-list parsing is a small branch over missing node, wildcard, or comma-separated values.

State and persistence behavior: persistent state is external XML only. The class does not cache the document or watch for changes, so updates require a new method call. Passwords are read as plaintext strings and retained in memory in `User` objects.

Dependencies and integration points: depends on `System.Windows.Forms.Application`, `System.Xml`, `System.IO`, `UserCollection`, and `ShareSettings`. It is tightly coupled to the sample executable layout and the XML schema `Settings/Users/User` plus `Settings/Shares/Share`.

Risks: missing files, missing nodes, missing attributes, malformed XML, or blank `Accounts` strings throw runtime exceptions. Wildcard access maps to a hard-coded `Users` group, which may not match all deployments. Plaintext password storage is a security concern, and comma splitting does not trim whitespace.

Test signals: no local tests in this item. Useful tests would cover wildcard and comma access lists, absent optional access nodes, missing required attributes, reload behavior after XML changes, and path resolution relative to the executable.
