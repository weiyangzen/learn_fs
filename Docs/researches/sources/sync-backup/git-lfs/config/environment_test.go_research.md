<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/git-lfs/config/environment_test.go -->
# sources/sync-backup/git-lfs/config/environment_test.go

## Research

This unit test file validates the `Environment` wrapper and conversion helpers. It confirms that `Get` returns the last value from a multi-value `MapFetcher`, `GetAll` preserves the value slice, unset booleans use their default, recognized truthy/falsy strings map correctly, and integer parsing returns defaults for blank or malformed values.

There is no persistence or external dependency. The tests are important because the same conversion rules drive LFS behavior flags such as transfer selection, prompts, cache credentials, and repository permissions. Remaining gaps include `Int64`, `All`, delayed environments, OS fetch caching, case sensitivity, and the intentionally surprising behavior where unknown boolean strings return `false` instead of the caller default.
<!-- END_FILE_RESEARCH: sources/sync-backup/git-lfs/config/environment_test.go -->
