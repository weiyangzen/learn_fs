# sources/test-tools/syzkaller/pkg/aflow/testdata/TestValidatedLLMReply.llm.json

## Purpose
Golden LLM request fixture for validating plain-text LLM replies rather than structured tool outputs.

## Important Data and APIs
The JSON array contains two model requests. The first has instruction and prompt only. The second appends the prior bad reply and a verification-failure message telling the model to correct the reply.

## Control Flow
The modeled flow is initial model call, validator rejects `reply1`, then retry prompt includes the rejection reason before asking for a corrected response.

## State and Persistence Behavior
Static serialized request history; no mutable state or external persistence beyond repository testdata.

## Dependencies and Integration Points
Used by aflow LLM-agent tests that verify retry prompt construction for reply validators. It depends on stable genai request JSON and validator-feedback wording.

## Risks and Test Signals
Risk is accidental loss of the previous reply or changed error prompt shape. The exact fixture is a regression signal for conversational retry context.
