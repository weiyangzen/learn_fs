<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/aflow/testdata/TestToolInPrompt.llm.json -->
# Research: sources/test-tools/syzkaller/pkg/aflow/testdata/TestToolInPrompt.llm.json

## Purpose
This request fixture backs `TestToolInPrompt`. It verifies that tool template placeholders can be rendered in both the agent instruction and prompt before the request is sent.

## Important APIs, Types, and Functions
It exercises `LLMAgent.Instruction`, `LLMAgent.Prompt`, the template helper that exposes tools as `.toolSwissKnife`, and `NewFuncTool` declaration for `swiss-knife`.

## Control Flow
The array contains 1 request. The system instruction is rendered as `Use swiss-knife` plus the multiple-tools hint. The prompt is rendered as `Please call swiss-knife now.` The tool declaration is still included, although the mocked model replies with text directly.

## State and Persistence
The file persists rendered prompt/config state and verifies there are no unresolved template markers. It does not persist execution state beyond the outbound request.

## Dependencies and Integration Points
It integrates with aflow template rendering, tool-name normalization for template variables, and genai request construction. The trajectory confirms the agent can finish without actually using the prompted tool.

## Risks
A template helper regression could leave `{{.toolSwissKnife}}` unresolved or render the wrong tool name. This would degrade prompts and potentially confuse model tool calls.

## Test Signals
Expected signals are one request, rendered text containing `swiss-knife`, a valid `swiss-knife` tool declaration, and no function call history.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/aflow/testdata/TestToolInPrompt.llm.json -->
