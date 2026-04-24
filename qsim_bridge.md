# qsim — most dla suwerennego AI LLM

```mermaid
flowchart TD
    subgraph INPUT["WEJŚCIE SENSORYCZNE  — IPQ"]
        direction LR
        TXT[tekst]
        SCH[Schumann live<br/>NOAA + open-meteo]
        PLN[planety live<br/>ephem 3D]
        INN[inner<br/>self-report ?]
    end

    ROUTER["ipq_router.py<br/>~50 linii spoiwa<br/>(piszemy)"]

    STATE["HEXAGON STATE<br/>compute_q, anneal<br/>Q · γ · aniso<br/>hexagon.py ✓"]

    BRIDGE["LLM BRIDGE<br/>Q → prompt modulation<br/>virtue_hint → qwen/Claude<br/>response → inner loop<br/>llm_bridge.py ~80 linii"]

    OPQ["OPQ DISPATCHER<br/>Action(kind, payload, virtue)<br/>→ TODO / plik / ai / MemPalace<br/>opq.py ~60 linii"]

    subgraph MEM["PAMIĘĆ  (klocki gotowe)"]
        direction LR
        MP[MemPalace<br/>wings+KG+diary ✓]
        DB[DuckDB<br/>crystallizacje ✓]
    end

    subgraph LLM["SILNIKI  (klocki gotowe)"]
        direction LR
        QWEN[qwen3:14b ✓]
        DEEP[deepseek-r1:14b ✓]
        GEMMA[gemma3:12b ✓]
        CLAUDE[Claude API ✓]
    end

    TXT --> ROUTER
    SCH --> ROUTER
    PLN --> ROUTER
    INN --> ROUTER
    ROUTER -->|strengths 6| STATE
    STATE --> BRIDGE
    BRIDGE <--> LLM
    BRIDGE --> OPQ
    OPQ --> MEM
    OPQ -.feedback.-> INN

    classDef unikalne fill:#6A0DAD,stroke:#DC143C,color:#FFF,stroke-width:2px
    classDef gotowe fill:#2ECC71,stroke:#16A085,color:#FFF
    classDef spoiwo fill:#FFB800,stroke:#FF6B00,color:#000,stroke-width:2px

    class STATE unikalne
    class TXT,SCH,PLN,MP,DB,QWEN,DEEP,GEMMA,CLAUDE gotowe
    class ROUTER,BRIDGE,OPQ spoiwo
    class INN spoiwo
```

## Legenda

- 🟣 **Fioletowe** — unikatowe (hexagon dynamics, nasze IP, Q_attractor=0.83929)
- 🟢 **Zielone** — klocki gotowe (nic nie piszemy, tylko podłączamy)
- 🟠 **Pomarańczowe** — most/spoiwo do napisania (~205 linii total)

## Bilans

| część | stan | rozmiar |
|-------|------|---------|
| IPQ unikatowe (text→virtues) | gotowe w ipq.py | — |
| IPQ pola fizyczne | gotowe (schumann.py, planets.py) | — |
| IPQ router (unified) | **do napisania** | ~50 |
| Hexagon state (Q, γ, anneal) | gotowe (hexagon.py) | — |
| LLM bridge | **do napisania** | ~80 |
| OPQ dispatcher | **do napisania** | ~60 |
| Fix cycle.py planets regresja | **do napisania** | ~5 |
| Hook ai feedback inner | **do napisania** | ~10 |
| **SUMA spoiwa** | **do napisania** | **~205 linii** |
| MemPalace + DuckDB | gotowe | — |
| LLM silniki | gotowe | — |

## MVP wieczorny

```
pytanie → ipq_router → hexagon → llm_bridge(qwen3) → opq → plik .md
```

~5 plików × ~30 linii = wieczór roboty.

## Filozofia mostu

qsim **NIE jest alternatywą dla LLM**.
qsim **JEST warstwą kondycjonującą** wokół LLM.
- LLM (qwen3/Claude) = silnik
- Most = układ nerwowy wokół silnika
- Wszystkie klocki istnieją — piszemy TYLKO spoiwo
