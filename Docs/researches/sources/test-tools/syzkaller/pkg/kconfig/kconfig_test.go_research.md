## sources/test-tools/syzkaller/pkg/kconfig/kconfig_test.go

Purpose: unit coverage for Kconfig parser tree construction, dependency closure, selected-by relationships, and fuzz robustness.

Important APIs/types/functions: `TestParseKConfig`, `TestSelectedby`, and `TestFuzzParseKConfig`.

Control flow: tests parse inline Kconfig snippets and assert config maps, prompts, dependencies, and reverse select traversal.

State and persistence: mostly in-memory parse data; may use target metadata.

Dependencies and integration: exercises `ParseData`, `DependsOn`, and `SelectedBy`.

Risks: narrow samples cannot cover all Linux Kconfig grammar.

Test signals: good regression coverage for the parser subset syzkaller relies on.
