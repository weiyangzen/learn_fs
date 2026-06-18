## sources/test-tools/syzkaller/pkg/lore-relay/testdata/patch_moderation.in.json

Purpose: JSON fixture for template tests covering a patch moderation scenario.

Important data: contains dashboard poll-result fields for a patch that requires relay-generated body/subject and moderation-related commands/links.

Control flow: loaded by template tests, unmarshaled into dashboard structs, and passed to `RenderBody`/`GenerateSubject`.

State and persistence: static test fixture.

Dependencies and integration: coupled to `dashapi.ReportPollResult` JSON shape and golden expected output.

Risks: schema drift can break fixture unmarshalling. Fixture content should mirror realistic dashboard responses.

Test signals: protects patch moderation email rendering.
