# Recipe Step Autocompleter

[![Built with askThili](https://ask.thili.ai/api/v1/public/projects/tsycmws65j/badge.svg)](https://ask.thili.ai/b/tsycmws65j)

The Recipe Step Autocompleter is a command-line tool designed for home cooks. It helps prevent missed steps and ensures smooth recipe following by autocompleting incomplete instructions. This project leverages next-word prediction and text generation capabilities to suggest logical continuations for recipe instructions.

## What you are building

**Goal.** You will build a CLI tool called 'Recipe Step Autocompleter' that helps home cooks complete incomplete recipe instructions, ensuring smooth recipe following.

**Done when.** The project is done when you have a functional command-line interface where users can input a partial recipe step and receive logical next-word suggestions to complete it, based on a trained n-gram model.

## Milestones

Tick these off as you go, and commit after each one.

- [x] **1. Compile a corpus of cooking recipe instructions.**
      Hint: Use text preprocessing techniques to clean and prepare your recipe data.
- [x] **2. Implement n-gram counting and maximum-likelihood probabilities with smoothing.**
      Hint: Apply n-gram counting and maximum-likelihood estimation from the drill.
- [x] **3. Create a function to generate recipe step continuations.**
      Hint: Implement the text generation logic, sampling from predicted next words.
- [x] **4. Build a CLI for users to input partial steps and get suggestions.**
      Hint: Design a simple command-line interface for user input and output.

## Run it

You need Python 3.12 and Git.

### Windows PowerShell

```powershell
cd D:\recipe-step-autocompleter
py -3.12 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
Copy-Item .env.example .env
python -m app.cli hello
python -m pytest -q
```

If your shell blocks activation, allow it only for the current process:

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.\.venv\Scripts\Activate.ps1
```

### macOS or Linux

```bash
python3.12 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
python -m app.cli hello
pytest
```

## Commands

Show ranked next-word suggestions:

```powershell
python -m app.cli suggest "add the" --count 5
```

Generate a continuation:

```powershell
python -m app.cli generate "stir in" --count 10
python -m app.cli generate "add the" --count 10 --sample --seed 42
```

Extend a partial step interactively:

```powershell
python -m app.cli complete "add the" --count 5 --steps 3
```

For repeatable automated use, choose the first suggestion on every round:

```powershell
python -m app.cli complete "add the" --count 5 --steps 3 --choose 1
```

## Model implementation

Milestone 1 lowercases recipe instructions, extracts words, removes punctuation, and discards empty entries.
Milestone 2 trains a trigram model with add-alpha smoothing and backs off to shorter contexts when needed.
Milestone 3 generates deterministic or seeded sampled continuations.
Milestone 4 exposes the `suggest`, `generate`, and `complete` commands.

## Settings and secrets

Model settings live in `.env`, which is ignored by git. **Never commit `.env` or paste a key into code.** If a key ever
reaches GitHub, treat it as leaked and make a new one.

## Stretch ideas

- Allow users to specify the number of continuation suggestions.
- Display the probability score alongside each suggested word.
- Enable users to select a suggested word to append to their input and get further suggestions.
