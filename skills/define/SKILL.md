---
name: define
description: Define a term or set of terms concisely in 250 words or fewer by classifying and structuring the definition across intensional, extensional, and ostensive frameworks. Use when the user types /define or asks to strictly define a concept, term, or set of terms without information overload.
---

# Define

Define a term or set of terms based on its semantic statement in 250 words or fewer. Prevent context overload by classifying the definition into intensional, extensional, and ostensive components before delivering a tight explanation.

## When to Use

- The user invokes `/define` followed by a term, phrase, or list of terms.
- The user asks for a strict, bounded definition of a concept without extra background noise.

## Steps

1. **Parse the target terms.** Identify the exact term or set of terms from the prompt.
2. **Select the definition classification.** Determine which framework best fits the semantic nature of the term, or combine them concisely:
   - **Intensional definition**, which specifies the necessary and sufficient conditions or properties that give the sense of a term.
   - **Extensional definition**, which lists the specific objects, members, or subclasses that fall under the term.
   - **Ostensive definition**, which conveys the meaning of the term by pointing directly to a concrete real-world example or instance.
3. **State the classification.** Open directly by naming the term and stating which definition category or combination applies.
4. **Deliver the bounded definition.** Write the semantic definition clearly and directly. If multiple terms are requested, allocate word count proportionally across all terms.
5. **Enforce the length ceiling.** Verify that the entire output contains 250 words or fewer before finishing.

## Output Format

**Term:** [Term Name]
**Classification:** [Intensional / Extensional / Ostensive]

**Intensional Sense:** [1 to 2 sentences stating the core properties and rules that define the term]
**Extensional Scope:** [Concise list or sentence naming the concrete objects or variants the term covers]
**Ostensive Example:** [1 concrete, real-world instance that demonstrates the term in action]

*(Omit a sub-label if only a single category applies to the term, and keep the total output across all requested terms strictly at or below 250 words.)*

## Gotchas

- **Exceeding the 250-word limit.** Never write more than 250 words total, even when the user supplies multiple terms. Shrink explanations to their core semantic properties if multiple terms compete for space.
- **Unclassified definitions.** Never output a generic dictionary definition without explicitly identifying whether the explanation operates intensionally, extensionally, or ostensively.
- **Preamble noise.** Start immediately with the definition structure. Do not include introductory filler or closing summaries.
