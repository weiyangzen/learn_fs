<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/notification/notifytemplate/repotemplate.go -->
# sources/sync-backup/kopia/notification/notifytemplate/repotemplate.go

- Purpose: Stores, lists, resolves, and deletes notification template overrides in repository manifests.
- Important APIs/types/functions: `ManifestType`, `TemplateManifest`, `Info`, `ResolveTemplate`, `GetTemplate`, `ListTemplates`, `SetTemplate`, `ResetTemplate`, `labelsFor`.
- Control flow: Resolution checks profile-specific override, generic override, then embedded template. Get loads latest matching manifest. List merges embedded templates and repository overrides filtered by prefix. Set replaces matching manifests; reset deletes matching overrides.
- State and persistence: Template overrides persist as repository manifests with type `notificationTemplate` and `template` labels.
- Dependencies and integration points: Used by notification senders before parsing/executing templates; integrates `repo`, `manifest`, and embedded template lookup.
- Risks and edge cases: List order is map-derived and not sorted here; template names are label values and lack validation in this file.
- Test signals: Rendering tests cover embedded templates; repository override behavior is not directly tested in this subset.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/notification/notifytemplate/repotemplate.go -->
