## sources/test-tools/syzkaller/pkg/lore-relay/testdata/reply_quote.in.json

Purpose: JSON fixture for reply rendering and quote formatting.

Important data: contains reply thread fields and quoted text inputs.

Control flow: template tests render replies and compare to expected output, exercising `quote` and reply subject logic.

State and persistence: static test input.

Dependencies and integration: tied to dashboard reply result JSON shape.

Risks: schema/template drift requires fixture and golden updates.

Test signals: protects outgoing reply email formatting.
