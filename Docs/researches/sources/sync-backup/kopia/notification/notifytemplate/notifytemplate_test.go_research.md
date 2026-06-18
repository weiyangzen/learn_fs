<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/notification/notifytemplate/notifytemplate_test.go -->
# sources/sync-backup/kopia/notification/notifytemplate/notifytemplate_test.go

- Purpose: Golden-tests embedded notification template rendering.
- Important APIs/types/functions: `defaultTestOptions`, `altTestOptions`, `TestNotifyTemplate_generic_error`, `TestNotifyTemplate_snapshot_report`, `TestNotifyTemplate_snapshot_report_single_success`, `verifyTemplate`.
- Control flow: Tests build representative notification args, force event time/hostname, render text/html templates under default and alternate timezone/format options, compare to expected files, and remove actual files on success.
- State and persistence: Writes `.actual` golden-output files under testdata, removing them only when output matches.
- Dependencies and integration points: Integrates `notification.MakeTemplateArgs`, `notifydata`, `notifytemplate`, `fs`, and `snapshot`.
- Risks and edge cases: Failed tests leave actual files by design; output comparisons are exact and sensitive to template formatting.
- Test signals: Direct coverage for embedded templates and helper functions used by rendering.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/notification/notifytemplate/notifytemplate_test.go -->
