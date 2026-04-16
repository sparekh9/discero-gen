# discero-gen

Agentic course generator for [Discero](https://discero.vercel.app/). Runs locally with your preferred LLM API key (and optional Tavily key), produces a single `course.json` that you upload to Discero via the Import Course page.

## Why

`discero-gen` enables generation through a local CLI that users run themselves, so the web app becomes a pure learning UI and the generation pipeline can be customized so long as the schema is followed.

## Install

```bash
git clone https://github.com/sparekh9/discero-gen.git
cd discero-gen
python -m venv .venv
# Windows
.venv\Scripts\activate
# macOS / Linux
source .venv/bin/activate
pip install -e .
```

Requires Python 3.11+.

## Setup

Copy `.env.example` to `.env` and fill in:

```
OPENAI_API_KEY=sk-...        # required
TAVILY_API_KEY=tvly-...      # optional; falls back to Wikipedia + arXiv only
```

`.env` is loaded automatically. You can also export the variables in your shell.

## Usage

```bash
discero create \
  --title "Cold War History" \
  --subject history \
  --duration 6 \
  --difficulty intermediate \
  --out ./cold-war.json
```

Flags:

| Flag | Default | Notes |
| --- | --- | --- |
| `--title` | required | Course title |
| `--subject` | required | Free text; used for tone + research routing (e.g. `math`, `history`, `biology`) |
| `--duration` | required | Course length in weeks (≥1) |
| `--difficulty` | `intermediate` | `beginner` \| `intermediate` \| `advanced` |
| `--out` | `./course.json` | Output path |
| `--model` | `gpt-4o-2024-08-06` | Primary model for outline, chapter content, seminar |
| `--mini-model` | `gpt-4o-mini` | Cheaper model for flashcards, quiz |
| `--no-research` | off | Skip the research step entirely |

### Other commands

```bash
discero validate ./cold-war.json   # validate without calling the model
discero version                    # print discero@<version>
```

## Importing into Discero

1. Open Discero, sign in.
2. Navigate to **Dashboard → Import Course**.
3. Drag and drop the `course.json` you just generated.
4. Review the preview, pick visibility, click **Import Course**.

Discero validates the file again on its side. If validation fails, the web app shows the exact field path — easy to fix and re-run.

## Schema

Top-level shape:

```jsonc
{
  "schemaVersion": 1,
  "generatedBy": "discero@0.1.0",
  "generatedAt": "2026-04-15T10:00:00Z",
  "course": {
    "subject": "history",
    "duration": 6,
    "outline": { /* title, description, learningObjectives, prerequisites, estimatedHours, chapters[], gamePlan */ },
    "chapters": [
      {
        "index": 0,
        "chapterData": { /* title, description, estimatedTime, learningGoals[], topics[] */ },
        "content": { /* introduction, sections[], exercises[], summary, nextSteps */ },
        "flashcards": [ /* { front, back } */ ],
        "quiz": [ /* { question, options[], correct, explanation } */ ],
        "seminar": { /* humanities only: topics[], viewpoints[] */ }
      }
    ]
  }
}
```

discero-gen is a [LangGraph](https://langchain-ai.github.io/langgraph/) pipeline:

```
research → outline → chapter_loop → finalize
```

- **research** — queries Wikipedia, arXiv, and (if available) Tavily, returns grounded notes.
- **outline** — structured-output OpenAI call producing title, description, objectives, chapters, game plan.
- **chapter_loop** — for each chapter, three structured-output calls: content, flashcards, quiz.
<!-- - **seminar** — humanities only. Emits debate topics and agent viewpoints attached per-chapter. -->
- **finalize** — assembles and Pydantic-validates the final `course.json`.

All LLM calls use structured outputs (`response_format={"type": "json_schema", ...}`) so the JSON is schema-correct by construction.

## License

MIT. See [LICENSE](LICENSE).
