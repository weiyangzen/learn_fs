<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/notification/notifytemplate/embeddedtemplate.go -->
# sources/sync-backup/kopia/notification/notifytemplate/embeddedtemplate.go

- Purpose: Embeds built-in notification templates and defines template helper functions/options.
- Important APIs/types/functions: `embedded`, `TestNotification`, `Options`, `formatCount`, `functions`, `DefaultOptions`, `GetEmbeddedTemplate`, `SupportedTemplates`, `ParseTemplate`.
- Control flow: Embedded FS provides `.html` and `.txt` templates. `functions` installs byte/count delta helpers, HTML delta helpers, snapshot sorting, and timezone-aware time formatting. `ParseTemplate` attaches helpers before parsing text.
- State and persistence: Built-in templates are embedded at compile time; rendering options are caller-provided.
- Dependencies and integration points: Integrates `units`, `notifydata`, `text/template`, and notification sending.
- Risks and edge cases: Template helper names are part of repository override compatibility; default timezone uses `time.Local`.
- Test signals: `notifytemplate_test.go` executes generic-error and snapshot-report templates against golden files.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/notification/notifytemplate/embeddedtemplate.go -->
