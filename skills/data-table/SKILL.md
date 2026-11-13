---
name: data-table
description: Builds adaptive data tables that externalize the mapping between terms and their roles so the reader no longer rebuilds it from prose. Use when linear text fails to maintain separation of concerns, when the user asks for a table to clarify concepts in any domain, or when a mental model needs fixed columns that match the specific context.
---

# Data Table — Separate Concerns for Mental Models

Build a table that holds multiple entities or terms against a shared set of attributes so comparison happens by scanning rather than by mental reconstruction.

## Core Workflow

1. Extract the exact list of terms or entities the user named. Do not add items the user did not request.
2. Determine the columns from the user's request or from the context of what they need to separate. Prefer columns the user stated. When the user does not state columns, choose the minimal set that separates the roles they are struggling to keep distinct. Common useful columns include plain-language definition, the problem the term removes, the concrete situation in which it applies, and the layer or location where it operates, but only when those distinctions match the domain.
3. Write one row per term. Keep each cell to one or two short sentences. Start from the known flaw in the usual explanation, then state the mechanical role.
4. Output the result as a single Markdown table. Place no surrounding narrative that re-embeds the same facts. A one-sentence lead that names the terms is allowed only if the user asked for context.
5. If the user supplied a partial table or different columns, keep their columns and fill only the missing cells.

## Column Selection

Columns must adapt to the domain and the user's stated need. In a history discussion the columns might be date, actors, and outcome. In a programming discussion they might be input type, failure mode, and return value. In a business discussion they might be cost driver, constraint, and measurable effect. It can vary based on the subject and what the user is trying to understand.

## When Not to Use

Drop the table when the user is following a sequential story, a causal chain, or a single entity. The grid is only for simultaneous comparison of multiple terms that share the same attribute set.