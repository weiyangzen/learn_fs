# sources/user-network-fs/rclone/lib/http/template.go

Source read signal: reviewed complete local file (140 lines, sha256 afe0ae64f734ad4a).

Purpose: Provides help/configuration and parsing for custom HTML directory-listing templates.

Important APIs/types/functions: Exports `TemplateHelp`, `TemplateConfigInfo`, `TemplateConfig`, flag methods, `DefaultTemplateCfg`, `AfterEpoch`, embedded `Assets`, and `GetTemplate`.

Control flow: `TemplateHelp` renders prefix-aware docs. `GetTemplate` reads either an embedded default `templates/index.html` or a user-provided path, registers helper funcs (`afterEpoch`, `contains`, `hasPrefix`, `hasSuffix`), and parses the template.

State and persistence behavior: Embedded assets are read-only; parsed templates are returned to callers and held by `Server`.

Dependencies and integration points: Uses `embed`, `html/template`, `os`, `strings`, `time`, rclone flags/options, and serve directory data fields.

Risks and test signals: User templates can fail parse at server init. Helper names are part of the documented template contract; tests only check help prefix, while directory tests render a golden template.
