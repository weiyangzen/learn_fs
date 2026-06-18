## sources/user-network-fs/gcsfuse/.gemini/config.yaml

Purpose: Configures Gemini Code Assist behavior for the gcsfuse repository.

Important APIs/types/functions: YAML key `code_review.pull_request_opened` enables `code_review` and `summary`, while `include_drafts: false` suppresses draft PR reviews.

Control flow: declarative only. Gemini Code Assist reads this file on PR-open events and decides whether to produce review and summary output.

State and persistence: no repo state is mutated by the file itself; generated review comments/summaries persist in GitHub PR metadata.

Dependencies and integration points: consumed by Gemini Code Assist for GitHub. The inline comment links to the official customization guide.

Risks: config is narrow and event-specific; edits can unintentionally silence automated review or enable draft noise. YAML indentation must remain valid.

Test signals: validation is operational through opening a non-draft PR and confirming Gemini review plus summary behavior.
