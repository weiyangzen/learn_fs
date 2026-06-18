# File Research: sources/virtualization/spdk/lib/nvme/nvme_discovery.c

This file implements asynchronous retrieval of the NVMe-oF discovery log page with generation-counter consistency checking.

`spdk_nvme_ctrlr_get_discovery_log_page()` allocates a discovery context plus an initial one-page discovery log buffer, then submits Get Log Page for `SPDK_NVME_LOG_DISCOVERY`. `discovery_log_header_completion()` validates that the completion is not an error, checks `recfmt == 0`, records the starting `genctr`, reads `numrec`, reallocates the buffer to hold all advertised entries when needed, and submits a second Get Log Page for the full page.

After the full page is fetched, `get_log_page_completion()` submits another small Get Log Page request to read the latest generation counter into `end_genctr`. `get_log_page_completion_final()` compares `start_genctr` and `end_genctr`: if they match, the callback receives the allocated log page; if they differ, the page is freed and retrieval restarts by calling `spdk_nvme_ctrlr_get_discovery_log_page()` again.

Errors are delivered through the caller callback with either a completion pointer or an integer error and null page. Memory ownership is important: on success the callback receives `ctx->log_page`; on failure or restart the file frees the buffer itself. The implementation assumes callers understand the asynchronous callback contract and that a changing discovery controller may force repeated retries.
