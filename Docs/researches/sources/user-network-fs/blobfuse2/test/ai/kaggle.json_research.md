<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/blobfuse2/test/ai/kaggle.json -->
# sources/user-network-fs/blobfuse2/test/ai/kaggle.json

## Purpose
Template Kaggle API credential file for AI dataset download tests.

## Important APIs, Types, and Functions
Contains JSON keys `username` and `key`, with the key shown as a placeholder.

## Control Flow and State
No executable flow. If placed where the Kaggle client expects it, it controls Kaggle API authentication.

## Dependencies and Integration Points
Used by the `kaggle` Python package and `kaggle_download.py` when authenticating.

## Risks and Edge Cases
Credential files should not contain real secrets in source control. The sample includes a real-looking username and placeholder key; users must replace securely and set file permissions as required by Kaggle tooling.

## Test Signals
Kaggle authentication success is the only practical validation.
<!-- END_FILE_RESEARCH: sources/user-network-fs/blobfuse2/test/ai/kaggle.json -->
