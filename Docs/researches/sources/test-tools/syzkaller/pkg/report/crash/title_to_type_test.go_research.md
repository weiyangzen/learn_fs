# sources/test-tools/syzkaller/pkg/report/crash/title_to_type_test.go

Purpose: Validates structural correctness of crash-title prefix definitions.

Important tests and helpers: `TestTitleToTypeDefinitions` iterates over `titleToType`, ensuring each definition has prefixes, no prefix is empty, no duplicate prefix exists, and no new prefix is already matched by a previously seen broader prefix. `hasPrefix` performs the shadowing check.

Control flow and state: The test relies on the production ordering of `titleToType`, matching the first-prefix-wins behavior in `TitleToType`.

Dependencies and integration: Protects `report/crash` classification from accidental shadowing and duplicate definitions.

Risks: It does not assert specific title-to-type examples or type group predicate behavior. It can reject intentional broad-before-specific changes unless ordering is updated.

Test signals: Strong guard for the most common maintenance error in ordered prefix tables.
