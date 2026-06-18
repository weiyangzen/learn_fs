# sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/resources/webapps/recon/ozone-recon-web/src/v2/pages/assistant/components/ModelPicker.tsx

Purpose: Provider/model selection controls for Recon AI requests.

Important APIs, types, and functions: Exports `ModelPicker` with model list, selected provider/model, provider/model change callbacks, and disabled flag.

Control flow: Groups models by provider using `getProviderForModel`, lists available providers plus the default sentinel, and shows a model select only after a non-default provider is selected.

State and persistence behavior: No local state; grouping is memoized from props.

Dependencies: Uses AntD `Select`, chatbot provider constants/helpers.

Integration points: Embedded in Composer and feeds provider/model to `useChat.sendMessage`.

Risks and edge cases: Unknown-provider models are grouped into `other` only if the group exists; current groups do. Prefix classification can be stale. Model select disappears when default provider is selected, losing selected model.

Test signals: Cover grouping, default sentinel, provider-specific model list, disabled state, unknown models, and provider/model callback values.
