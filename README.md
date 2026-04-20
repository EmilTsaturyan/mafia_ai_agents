# 🎭 AI Mafia Multi-Agent Game

## 📌 Overview

This project is a **multi-agent Mafia game simulation** where each player is powered by an LLM (AI agent). Each agent has a role, memory, and strategy, and interacts with others to achieve its goal.

The system is designed to simulate **realistic social reasoning, deception, and decision-making**.

---

## 🧠 Core Concepts

### 1. Game Engine (Backend Logic)

Controls:

* Game phases (Introduction, Night, Day, Vote)
* Player states (alive/dead)
* Role assignments
* Action validation
* Win conditions

---

### 2. AI Agents

Each player is an independent AI agent with:

* Role (Mafia, Sheriff, Doctor, Civilian)
* Personality
* Memory (history of events)
* Private information

Agents:

* Analyze game state
* Generate actions
* Communicate with other players

---

### 3. Game Phases

#### Introduction

* Players introduce themselves

#### Night

* Mafia → kill
* Sheriff → check
* Doctor → heal

#### Day

* Discussion phase
* Players analyze and accuse

#### Vote

* Players vote to eliminate someone

---

## 📚 History System

### Structure

```python
class History:
    type: str  # introduce, speech, vote, kill, heal, check, kicked
    player: str
    target: Optional[str]
    text: Optional[str]
```

### Example

```python
{
  "type": "vote",
  "player": "Player1",
  "target": "Player3",
  "text": "I think Player3 is suspicious"
}
```

---

## 🤖 Agent Input

Each turn, agent receives:

* Role
* Current phase
* Alive players
* Game history
* Private info

---

## 🧾 Agent Output (Structured)

```json
{
  "action": "vote | kill | heal | check | speak | introduce | skip",
  "target": "player_name or null",
  "message": "string"
}
```

---

## 🧠 Prompt Design

### System Prompt (static)

Contains:

* Game rules
* Role behavior
* Strategy guidelines
* Output format

### Dynamic Input (per turn)

```text
Role: {role}
Phase: {phase}
Alive players: {alive_players}
History: {history}
Private info: {private_info}
```

---

## 🧠 Strategy Layer (Advanced)

Agents should:

* Think strategically, not just logically
* Consider suspicion levels
* Avoid exposing their role
* Bluff and manipulate (for Mafia)

---

---

## 🔥 Improvements Roadmap

* [ ] Add trust/suspicion system
* [ ] Add long-term memory per agent
* [ ] Improve Mafia deception strategies
* [ ] Add UI (web or Telegram)
* [ ] Run simulations (100+ games)
* [ ] Analytics (win rates, behavior patterns)

---

## 🚀 Architecture

```
Game Engine
   ↓
Prompt Builder
   ↓
LLM Agent
   ↓
Structured Action
   ↓
Validator
   ↓
Game State Update
```

---

## 💡 Key Principles

* Prompt = guidance
* Code = rules
* Validation = safety
* Memory = intelligence
* Personality = realism

---

## 🎯 Goal

Create a system where agents:

* Reason
* Deceive
* Adapt
* Compete

Just like real Mafia players.

---

## 🧪 Example Use Cases

* AI behavior research
* Multi-agent systems
* Game simulations
* LLM reasoning experiments

---

## 📦 Tech Stack (Suggested)

* Python
* Pydantic
* Any LLM provider (Gemini / OpenAI / etc.)

---

