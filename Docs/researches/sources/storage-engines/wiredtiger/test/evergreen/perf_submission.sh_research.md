<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/evergreen/perf_submission.sh -->
# sources/storage-engines/wiredtiger/test/evergreen/perf_submission.sh

Purpose: submits Cedar-style performance result JSON to MongoDB's Signal Processing Service/raw performance endpoint.

Control flow: derives `is_mainline` from Evergreen `requester == commit`, extracts a username/order suffix from `revision_order_id`, then POSTs `${perf_file_path}` to a URL containing project, version, variant, order, task name/id, execution, and mainline query parameters. It appends `HTTP_STATUS` to curl output, separates status and response body, exits nonzero unless status is 200, and prints the response body/status.

State and persistence: no local writes. Sends performance data over HTTP to a corp endpoint.

Dependencies and integration: referenced by Evergreen performance tasks after perf JSON is generated. Requires Evergreen expansions such as `project_id`, `version_id`, `build_variant`, `task_name`, `task_id`, `execution`, `revision_order_id`, and `perf_file_path`.

Risks and test signals: unquoted `@${perf_file_path}` and URL variables require sane values. Only HTTP 200 is accepted. Network or service outages fail the task. The script assumes patch revision order IDs append username after underscores.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/evergreen/perf_submission.sh -->
