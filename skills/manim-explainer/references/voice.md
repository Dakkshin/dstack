# Narration: writing and directing it so it sounds spoken

Read this before writing `narration.py`. If `NARRATION_STYLE` (skill `.env`) or `STYLE`
(`narration.py`) names a style guide, read that too and write in its plain, spoken mode. Where
the two disagree on wording, the style guide wins. This file covers delivery, which a writing
guide usually doesn't.

## Why narration sounds robotic

Two separate failures, and both need fixing.

1. **One tone throughout.** Real speakers don't hold a pitch. Across a topic, pitch starts
   high and wide, drifts down (by roughly 10 to 20 percent across a unit of speech), and the
   unit ends slower and lower, followed by a longer pause. The next topic starts with a reset
   to a higher pitch and a wider range. Linguists call that spoken paragraph a *paratone*. TTS
   models tend to learn the average intonation, because they treat this variation as noise, so
   left alone they produce the flat middle of it.
2. **Text written for the eye.** Spoken explanation uses contractions, plainer syntax and
   *discourse markers*, which are the "so", "now", "okay" and "right" that tell a listener
   where they are. In lectures, "so" and "now" mark a topic shift, and "okay" and "right"
   open and close one. In unplanned dialogue, about 44 percent of turns start with one. A
   script with none of them sounds read aloud, because it is.

The pipeline already fixes a third failure, which is clips that restart every sentence. Each
scene is one take, cut into beats at its natural pauses (see `scripts/tts.py`).

## Shape every scene as a paratone

| part of the scene | what the voice does | how to write it |
|---|---|---|
| opening beat | resets higher, more energy | a discourse marker ("So", "Now", "Okay") or a question, and one lifting tag (`[curious]`, `[excited]`, `[warmly]`) |
| middle beats | a steady explaining line, stressing what's new | plain sentences. Stress the one new word per beat in CAPS. An ellipsis before a turn ("...and now the ruler has moved") |
| closing beat | settles, slower and lower | a shorter sentence that lands, and optionally a settling tag (`[thoughtful]`, `[softly]`, `[matter-of-fact]`) |

Stress what's new and let what's already been said go unstressed. "It's EXACTLY what the slow
way gave us" stresses the surprise, not "slow way", which the viewer already knows.

## Audio tags (eleven_v3 and eleven_v4)

Tags are plain-language directions in square brackets, performed by the model and never
spoken: `[curious]`, `[excited]`, `[thoughtful]`, `[amused]`, `[warmly]`, `[softly]`,
`[matter-of-fact]`, `[emphatic]`, `[sighs]`.

- Put a tag right before the words it should colour. It holds until the sentence ends or
  another tag replaces it.
- Use them at inflection points, which is about 1 to 3 per scene and at most 2 per beat. Tags
  in a dense run fight each other and the result gets unstable.
- The tag must match the words. `[excited]` on a sad line confuses the model.
- Tags amplify the voice's own character, so they can't turn a calm voice manic.
- Pauses come from punctuation (an ellipsis or a full stop) rather than pause tags, which
  destabilise output when overused. Don't use dashes, because the owner's style bans them.
- Use CAPS for at most one word per beat. More than that sounds like shouting.

`eleven_multilingual_v2` would read tags aloud. When a project runs on it, `tts.py` strips
them, and the lint says so. `script.md` always shows the words without tags.

## Words that flow when spoken

- Use contractions everywhere ("it's", "doesn't", "you'd").
- Bridge ideas instead of leaving a bare-comma add-on ("which is", "in which", "and then").
- Define a new term in the sentence that introduces it, with a "which is" bridge.
- Let length swing. A long sentence sets up, and a short one lands. The lint flags three
  sentences in a row of about the same length.
- Ask the question the viewer is about to ask, then answer it.
- Speak numbers exactly, written the way they should be read ("1.21", "82.5 percent").
- Avoid filler ("basically", "really", "actually") and meta-narration ("Let's", "Note that",
  "In summary"). The video ends on the point said once more and more sharply, not on a recap.
- Read every beat aloud before building, and rewrite anything you wouldn't say to a colleague.

## The lint

`tts.py` prints a script lint before synthesis. It warns about, and never blocks on:
- dashes, arrows and symbols
- mid-sentence colons
- banned words (taken from the style guide when it's JSON)
- meta-narration
- uncontracted forms
- sentences over 30 words
- flat rhythm
- tag density
- more than one CAPS word per beat
- tags on a model that would read them aloud

## Sources

- Paratone, pitch reset and declination: Farrús et al., "Paragraph-based prosodic cues for
  speech synthesis", Speech Prosody 2016; Wikipedia, "Prosodic unit".
- Averaged intonation in TTS: "Perception of prosodic variation for speech synthesis"
  (arXiv:2003.06686).
- Discourse markers in lectures and spontaneous speech: Thai university lecture study (ERIC
  EJ1242989); Heeman et al., "Identifying discourse markers in spoken dialog"
  (cmp-lg/9801002).
- Audio tags, pauses and emphasis: ElevenLabs, "Best practices" and "Audio Tags 101"; the
  Eleven v4 announcement (elevenlabs.io/v4).
